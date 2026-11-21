// Colossal Potato — ordering, capacity, distance pricing, driver + live tracking
const BOWLS = { chicken: ["Chicken Bacon Ranch", 7000], steak: ["Steakhouse Loaded", 9000], bbq: ["BBQ Chicken Stack", 6500], pork: ["Pulled Pork & Crispy Onion", 6500], sweet: ["Garden Sweet Potato", 5500], classic: ["Classic Loaded", 5000], country: ["Country Breakfast", 6500], supreme: ["Breakfast Supreme", 6500] };
const ADDS = { xchicken: ["+Chicken 4oz", 2000], xsteak: ["+Steak 4oz", 3000], bacon: ["Bacon", 1000], cheese: ["Extra cheese", 500], sourcream: ["Sour cream", 500], onions: ["Crispy onions", 500], mushrooms: ["Mushrooms", 500], lowcarb: ["Low-carb (cauliflower base)", 500] };
const WIN = { am: "9 – 11 AM", pm: "2 – 4 PM", eve: "7 – 9 PM" };
const WIN_END = { am: 11 * 60, pm: 16 * 60, eve: 21 * 60 };
const HOLD_MS = 20 * 60 * 1000;
const STOP_MIN = 4;
const STAGES = { prep: "Prepping", cook: "Cooking", ready: "Out for delivery" };
const UA = { "User-Agent": "ColossalPotato/1.0 (orders@colossalpotato.com)" };

const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json", "cache-control": "no-store" } });
const html = (h) => new Response(h, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
const rid = (n = 16) => [...crypto.getRandomValues(new Uint8Array(n))].map(b => b.toString(16).padStart(2, "0")).join("");

function laNow() {
  const p = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Los_Angeles", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false }).formatToParts(new Date());
  const g = t => p.find(x => x.type === t).value;
  return { date: `${g("year")}-${g("month")}-${g("day")}`, mins: (+g("hour") % 24) * 60 + +g("minute") };
}
function addDays(d, n) { const x = new Date(d + "T12:00:00Z"); x.setUTCDate(x.getUTCDate() + n); return x.toISOString().slice(0, 10); }
function windowErr(date, win) {
  const n = laNow();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date || "")) return "Pick a delivery date.";
  if (!WIN[win]) return "Pick a delivery window.";
  if (date < n.date) return "That date has passed.";
  if (date > addDays(n.date, 92)) return "You can preorder up to 3 months ahead.";
  if (win === "am") { if (date === n.date) return "Order by 7 PM the night before."; if (date === addDays(n.date, 1) && n.mins >= 1140) return "Past the 7 PM cutoff."; }
  if (win === "pm" && date === n.date && n.mins >= 660) return "Past the 11 AM cutoff.";
  if (win === "eve" && date === n.date && n.mins >= 900) return "Past the 3 PM cutoff.";
  return "";
}
function miles(a, b) { const R = 3958.8, r = x => x * Math.PI / 180; const dl = r(b.lat - a.lat), dn = r(b.lng - a.lng); const h = Math.sin(dl / 2) ** 2 + Math.cos(r(a.lat)) * Math.cos(r(b.lat)) * Math.sin(dn / 2) ** 2; return 2 * R * Math.asin(Math.sqrt(h)); }
const kitchen = env => ({ lat: +env.KITCHEN_LAT, lng: +env.KITCHEN_LNG });
const e164 = p => { const d = String(p || "").replace(/\D/g, ""); return d.length === 10 ? "+1" + d : d.length === 11 && d[0] === "1" ? "+" + d : ""; };
async function sms(env, to, body) {
  const num = e164(to); if (!num || !env.TWILIO_SID || !env.TWILIO_TOKEN || !env.TWILIO_FROM) return false;
  const r = await fetch(`https://api.twilio.com/2010-04-01/Accounts/${env.TWILIO_SID}/Messages.json`, { method: "POST", headers: { Authorization: "Basic " + btoa(`${env.TWILIO_SID}:${env.TWILIO_TOKEN}`), "Content-Type": "application/x-www-form-urlencoded" }, body: new URLSearchParams({ To: num, From: env.TWILIO_FROM, Body: body }) });
  return r.ok;
}
const site = env => env.SITE_URL || "https://colossalpotato.com";
const prettyDate = d => new Date(d + "T12:00:00Z").toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", timeZone: "UTC" });
function msgFor(env, o, kind) {
  const link = `${site(env)}/track/${o.token}`, first = String(o.name || "").split(" ")[0], when = `${prettyDate(o.date)}, ${WIN[o.win]}`;
  return {
    confirmed: `Colossal Potato: Thanks ${first}! Your ${o.bowls}-bowl order is confirmed for ${when}. Track it anytime: ${link}`,
    prep: `Colossal Potato: ${first}, we're prepping your order now for delivery ${WIN[o.win]} today. ${link}`,
    cook: `Colossal Potato: Your bowls are cooking fresh right now! Delivery ${WIN[o.win]}. ${link}`,
    ready: `Colossal Potato: Your order is packed and out for delivery! Watch your driver live: ${link}`,
    delivered: `Colossal Potato: Delivered! Keep refrigerated, best within 4 days. Enjoy, ${first}!`
  }[kind];
}

async function geocode(q) {
  const u = "https://nominatim.openstreetmap.org/search?" + new URLSearchParams({ q, format: "json", limit: "1", countrycodes: "us", addressdetails: "0" });
  const r = await fetch(u, { headers: UA }); if (!r.ok) return null;
  const j = await r.json(); if (!j.length) return null;
  return { lat: +j[0].lat, lng: +j[0].lon, label: j[0].display_name };
}
async function route(pts) {
  const c = pts.map(p => `${p.lng.toFixed(6)},${p.lat.toFixed(6)}`).join(";");
  const r = await fetch(`https://router.project-osrm.org/route/v1/driving/${c}?overview=false`, { headers: UA });
  if (!r.ok) return null; const j = await r.json(); if (!j.routes || !j.routes[0]) return null;
  return { meters: j.routes[0].distance, secs: j.routes[0].duration };
}
async function quote(env, address) {
  if (!address || address.length < 8) return { error: "Enter your full street address." };
  const g = await geocode(address + (/(ca|california)\b/i.test(address) ? "" : ", CA"));
  if (!g) return { error: "We couldn't find that address. Check the street, city and ZIP." };
  const rt = await route([kitchen(env), g]);
  const mi = rt ? rt.meters / 1609.34 : miles(kitchen(env), g) * 1.3;
  if (mi > 20) return { error: `That address is ${mi.toFixed(1)} driving miles away — we deliver within 20 miles.`, miles: +mi.toFixed(1) };
  return { miles: +mi.toFixed(1), zone: mi <= 10 ? 10 : 20, fee: mi <= 10 ? 700 : 1400, lat: g.lat, lng: g.lng, label: g.label };
}

async function booked(env, date) {
  const cut = Date.now() - HOLD_MS;
  const r = await env.DB.prepare("SELECT win, COALESCE(SUM(bowls),0) b FROM orders WHERE date=? AND (status IN ('paid','delivered') OR (status='pending' AND created>?)) GROUP BY win").bind(date, cut).all();
  const m = { am: 0, pm: 0, eve: 0 }; for (const x of r.results) m[x.win] = x.b; return m;
}
async function availability(env, date) {
  const capD = +(env.DAILY_CAP || 30), capW = +(env.WINDOW_CAP || 15);
  const b = await booked(env, date); const used = b.am + b.pm + b.eve; const dayLeft = Math.max(0, capD - used);
  const windows = {};
  for (const w of Object.keys(WIN)) {
    const left = Math.max(0, Math.min(capW - b[w], dayLeft)); const cut = windowErr(date, w);
    windows[w] = { label: WIN[w], left, open: !cut && left >= 5, reason: cut || (left < 5 ? "SOLD OUT" : "") };
  }
  return { date, dayLeft, windows };
}

function buildItems(items, cfg) {
  const BW = (cfg && cfg.bowls) || BOWLS, AD = (cfg && cfg.adds) || ADDS;
  let bowls = 0, sub = 0; const lines = [];
  for (const it of Array.isArray(items) ? items : []) {
    const bw = BW[it.id]; const packs = Math.floor(+it.packs);
    if (!bw || !(packs >= 1 && packs <= 6)) return { error: "Invalid item." };
    const adds = (Array.isArray(it.adds) ? it.adds : []).filter(a => AD[a] && !(it.id === "sweet" && a.startsWith("x")));
    const unit = bw[1] + adds.reduce((s, a) => s + AD[a][1], 0);
    const desc = [adds.map(a => AD[a][0]).join(", "), it.sauce === "side" ? "sauce on side" : "sauce drizzled"].filter(Boolean).join(" | ");
    lines.push({ id: it.id, name: `${bw[0]} — 5-pack`, desc, unit, qty: packs }); bowls += packs * 5; sub += unit * packs;
  }
  return { bowls, sub, lines };
}

async function checkout(req, env) {
  let b; try { b = await req.json(); } catch { return json({ error: "Bad request." }, 400); }
  const it = buildItems(b.items, await env.IMG.get("menu.json", "json")); if (it.error) return json(it, 400);
  if (!it.bowls) return json({ error: "Your cart is empty." }, 400);
  const name = String(b.name || "").trim().slice(0, 80), phone = String(b.phone || "").replace(/[^\d+]/g, "").slice(0, 15), email = String(b.email || "").trim().slice(0, 120);
  if (name.length < 2 || phone.length < 10) return json({ error: "Enter your name and a phone number we can text." }, 400);
  const err = windowErr(b.date, b.win); if (err) return json({ error: err }, 400);
  const av = await availability(env, b.date); const w = av.windows[b.win];
  if (it.bowls > w.left) return json({ error: w.left >= 5 ? `Only ${w.left} bowls left in that window.` : "That window is sold out — pick another time." }, 409);
  const q = await quote(env, String(b.address || "").slice(0, 200)); if (q.error) return json({ error: q.error }, 400);
  const fee = q.fee; const total = it.sub + fee;
  const test = env.UPLOAD_KEY && b.test === env.UPLOAD_KEY;
  if (!test && !env.STRIPE_SECRET_KEY) return json({ error: "Online ordering opens soon! Follow us for launch day." }, 503);
  const id = rid(8), token = rid(12);
  await env.DB.prepare("INSERT INTO orders (id,token,created,status,name,phone,email,address,lat,lng,miles,date,win,bowls,items,subtotal,fee,total) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
    .bind(id, token, Date.now(), test ? "paid" : "pending", name, phone, email, String(b.address).slice(0, 200), q.lat, q.lng, q.miles, b.date, b.win, it.bowls, JSON.stringify(it.lines), it.sub, fee, total).run();
  const origin = new URL(req.url).origin;
  if (test) { await sms(env, phone, msgFor(env, { token, name, date: b.date, win: b.win, bowls: it.bowls }, "confirmed")); return json({ url: `${origin}/thanks?t=${token}` }); }
  const f = new URLSearchParams();
  f.set("mode", "payment"); f.set("client_reference_id", id);
  f.set("success_url", `${origin}/thanks?t=${token}`); f.set("cancel_url", `${origin}/#checkout`);
  f.set("expires_at", String(Math.floor(Date.now() / 1000) + 31 * 60));
  if (email) f.set("customer_email", email);
  let i = 0;
  for (const l of it.lines) {
    f.set(`line_items[${i}][quantity]`, String(l.qty)); f.set(`line_items[${i}][price_data][currency]`, "usd");
    f.set(`line_items[${i}][price_data][unit_amount]`, String(l.unit)); f.set(`line_items[${i}][price_data][product_data][name]`, l.name);
    if (l.desc) f.set(`line_items[${i}][price_data][product_data][description]`, l.desc); i++;
  }
  if (fee) { f.set(`line_items[${i}][quantity]`, "1"); f.set(`line_items[${i}][price_data][currency]`, "usd"); f.set(`line_items[${i}][price_data][unit_amount]`, String(fee)); f.set(`line_items[${i}][price_data][product_data][name]`, `Delivery (${q.miles} mi)`); }
  const meta = { order_id: id, delivery: `${b.date} ${WIN[b.win]}`, address: String(b.address).slice(0, 200), phone, bowls: String(it.bowls) };
  for (const [k, v] of Object.entries(meta)) { f.set(`metadata[${k}]`, v); f.set(`payment_intent_data[metadata][${k}]`, v); }
  const r = await fetch("https://api.stripe.com/v1/checkout/sessions", { method: "POST", headers: { Authorization: `Bearer ${env.STRIPE_SECRET_KEY}`, "Content-Type": "application/x-www-form-urlencoded" }, body: f });
  const s = await r.json();
  if (!r.ok) { await env.DB.prepare("DELETE FROM orders WHERE id=?").bind(id).run(); return json({ error: "Payment setup failed. Please try again." }, 502); }
  await env.DB.prepare("UPDATE orders SET stripe_session=? WHERE id=?").bind(s.id, id).run();
  return json({ url: s.url });
}

async function stripeWebhook(req, env) {
  const body = await req.text(); const sig = req.headers.get("stripe-signature") || "";
  if (!env.STRIPE_WEBHOOK_SECRET) return new Response("not configured", { status: 400 });
  const parts = Object.fromEntries(sig.split(",").map(x => x.split("=")));
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(env.STRIPE_WEBHOOK_SECRET), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = [...new Uint8Array(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`${parts.t}.${body}`)))].map(b => b.toString(16).padStart(2, "0")).join("");
  if (mac !== parts.v1 || Math.abs(Date.now() / 1000 - +parts.t) > 600) return new Response("bad sig", { status: 400 });
  const ev = JSON.parse(body);
  if (ev.type === "checkout.session.completed" && ev.data.object.payment_status === "paid") {
    const s = ev.data.object;
    const res = await env.DB.prepare("UPDATE orders SET status='paid', email=COALESCE(NULLIF(email,''),?) WHERE id=? AND status='pending'").bind((s.customer_details || {}).email || "", s.client_reference_id).run();
    const o = await env.DB.prepare("SELECT * FROM orders WHERE id=?").bind(s.client_reference_id).first();
    if (o && res.meta && res.meta.changes) await sms(env, o.phone, msgFor(env, o, "confirmed"));
  }
  if (ev.type === "checkout.session.expired") await env.DB.prepare("UPDATE orders SET status='expired' WHERE id=? AND status='pending'").bind(ev.data.object.client_reference_id).run();
  return new Response("ok");
}

// ---------- delivery ordering ----------
async function routeOrders(env, date, win) {
  const r = await env.DB.prepare("SELECT id,name,phone,address,lat,lng,bowls,items,status,seq,delivered_at,stage FROM orders WHERE date=? AND win=? AND status IN ('paid','delivered')").bind(date, win).all();
  const list = r.results;
  if (list.some(o => o.seq == null)) {
    const left = list.slice(); let cur = kitchen(env), n = 1;
    const done = left.filter(o => o.status === "delivered").sort((a, b) => a.delivered_at - b.delivered_at);
    for (const o of done) { o.seq = n++; cur = o; left.splice(left.indexOf(o), 1); }
    while (left.length) { left.sort((a, b) => miles(cur, a) - miles(cur, b)); const o = left.shift(); o.seq = n++; cur = o; }
    await env.DB.batch(list.map(o => env.DB.prepare("UPDATE orders SET seq=? WHERE id=?").bind(o.seq, o.id)));
  }
  return list.sort((a, b) => a.seq - b.seq);
}

async function track(env, token) {
  const o = await env.DB.prepare("SELECT * FROM orders WHERE token=?").bind(token).first();
  if (!o) return { error: "Order not found." };
  const base = { name: o.name.split(" ")[0], date: o.date, window: WIN[o.win], bowls: o.bowls, items: JSON.parse(o.items || "[]").map(l => `${l.qty}× ${l.name}`), me: { lat: o.lat, lng: o.lng } };
  if (o.status === "pending") return { ...base, stage: "pending", msg: "Waiting for payment confirmation." };
  if (o.status === "delivered") return { ...base, stage: "delivered", msg: "Delivered — enjoy!", deliveredAt: o.delivered_at };
  if (o.status !== "paid") return { ...base, stage: o.status, msg: "This order is not active." };
  const d = await env.DB.prepare("SELECT * FROM driver WHERE id=1").first();
  const live = d && d.active && d.date === o.date && d.win === o.win && Date.now() - d.updated < 5 * 60 * 1000;
  if (!live) {
    const st = o.stage || "scheduled";
    const m = { scheduled: o.date === laNow().date ? "Confirmed — we'll start prepping soon." : `Confirmed for ${prettyDate(o.date)}. Tracking goes live when your driver heads out.`, prep: "Prepping your ingredients now.", cook: "Your bowls are cooking fresh! 🔥", ready: "Packed and ready — your driver is heading out." }[st];
    return { ...base, stage: st, msg: m };
  }
  const list = await routeOrders(env, o.date, o.win);
  const ahead = list.filter(x => x.status === "paid" && x.seq < o.seq);
  const car = { lat: d.lat, lng: d.lng };
  const atKitchen = miles(car, kitchen(env)) < 0.4;
  const ck = `eta:${token}`; let eta = await env.IMG.get(ck, "json");
  if (!eta) {
    const rt = await route([car, ...ahead.map(x => ({ lat: x.lat, lng: x.lng })), { lat: o.lat, lng: o.lng }]);
    const mins = Math.round((rt ? rt.secs / 60 : miles(car, o) * 2.5) + ahead.length * STOP_MIN);
    eta = { mins, at: Date.now() }; await env.IMG.put(ck, JSON.stringify(eta), { expirationTtl: 60 });
  }
  const mins = Math.max(1, eta.mins - Math.round((Date.now() - eta.at) / 60000));
  return { ...base, stage: atKitchen ? "packing" : "enroute", msg: atKitchen ? "Packing orders — heading out shortly." : (ahead.length ? `${ahead.length} stop${ahead.length > 1 ? "s" : ""} before you` : "You're next!"), stopsBefore: ahead.length, etaMins: mins, car: atKitchen ? null : car, updated: d.updated };
}

async function driverApi(req, env, path) {
  if (!env.DRIVER_KEY || req.headers.get("x-key") !== env.DRIVER_KEY) return json({ error: "Wrong driver code." }, 403);
  const b = req.method === "POST" ? await req.json().catch(() => ({})) : {};
  const u = new URL(req.url);
  if (path === "route") {
    const date = u.searchParams.get("date") || laNow().date, win = u.searchParams.get("win") || "pm";
    const list = await routeOrders(env, date, win); const d = await env.DB.prepare("SELECT * FROM driver WHERE id=1").first();
    return json({ date, win, label: WIN[win], driver: d, smsOn: !!env.TWILIO_SID, stops: list.map(o => ({ id: o.id, seq: o.seq, stage: o.stage, name: o.name, phone: o.phone, address: o.address, bowls: o.bowls, items: JSON.parse(o.items || "[]").map(l => `${l.qty}× ${l.name}${l.desc ? " (" + l.desc + ")" : ""}`), status: o.status })) });
  }
  if (path === "start") { await env.DB.prepare("UPDATE driver SET active=1, date=?, win=?, updated=? WHERE id=1").bind(b.date, b.win, Date.now()).run(); return json({ ok: true }); }
  if (path === "stop") { await env.DB.prepare("UPDATE driver SET active=0 WHERE id=1").run(); return json({ ok: true }); }
  if (path === "ping") { if (typeof b.lat !== "number") return json({ error: "no fix" }, 400); await env.DB.prepare("UPDATE driver SET lat=?, lng=?, updated=? WHERE id=1").bind(b.lat, b.lng, Date.now()).run(); return json({ ok: true }); }
  if (path === "delivered") {
    const r = await env.DB.prepare("UPDATE orders SET status='delivered', delivered_at=? WHERE id=? AND status='paid'").bind(Date.now(), b.id).run();
    if (r.meta && r.meta.changes) { const o = await env.DB.prepare("SELECT * FROM orders WHERE id=?").bind(b.id).first(); await sms(env, o.phone, msgFor(env, o, "delivered")); }
    return json({ ok: true });
  }
  if (path === "stage") {
    if (!STAGES[b.stage]) return json({ error: "bad stage" }, 400);
    const r = await env.DB.prepare("SELECT * FROM orders WHERE date=? AND win=? AND status='paid' AND COALESCE(stage,'') <> ?").bind(b.date, b.win, b.stage).all();
    await env.DB.prepare("UPDATE orders SET stage=? WHERE date=? AND win=? AND status='paid'").bind(b.stage, b.date, b.win).run();
    let sent = 0; for (const o of r.results) if (await sms(env, o.phone, msgFor(env, o, b.stage))) sent++;
    return json({ ok: true, orders: r.results.length, texted: sent, sms: !!env.TWILIO_SID });
  }
  if (path === "undo") { await env.DB.prepare("UPDATE orders SET status='paid', delivered_at=NULL WHERE id=? AND status='delivered'").bind(b.id).run(); return json({ ok: true }); }
  return json({ error: "unknown" }, 404);
}

async function page(env, key, sub = {}) {
  let h = await env.IMG.get(key); if (!h) return new Response("Coming soon", { status: 404 });
  for (const [k, v] of Object.entries(sub)) h = h.split(k).join(v);
  return html(h);
}

export default {
  async fetch(req, env) {
    const u = new URL(req.url), p = u.pathname;
    try {
      if (p === "/api/availability") return json(await availability(env, u.searchParams.get("date") || laNow().date));
      if (p === "/api/quote" && req.method === "POST") { const b = await req.json().catch(() => ({})); const q = await quote(env, String(b.address || "").slice(0, 200)); return json(q.error ? q : { miles: q.miles, zone: q.zone, fee: q.fee }, q.error ? 400 : 200); }
      if (p === "/api/checkout" && req.method === "POST") return checkout(req, env);
      if (p === "/api/stripe-webhook" && req.method === "POST") return stripeWebhook(req, env);
      if (p.startsWith("/api/track/")) return json(await track(env, p.slice(11).replace(/[^a-f0-9]/g, "")));
      if (p.startsWith("/api/driver/")) return driverApi(req, env, p.slice(12));
      if (p.startsWith("/admin/put/") && req.method === "PUT") {
        if (!env.UPLOAD_KEY || req.headers.get("x-key") !== env.UPLOAD_KEY) return new Response("no", { status: 403 });
        const k = p.slice(11).replace(/[^a-z0-9._-]/gi, ""); await env.IMG.put(k, await req.arrayBuffer()); return new Response("ok " + k);
      }
      if (p.startsWith("/img/")) {
        const k = p.slice(5).replace(/[^a-z.]/g, ""); const v = await env.IMG.get(k, "arrayBuffer");
        if (!v) return new Response("Not found", { status: 404 });
        return new Response(v, { headers: { "content-type": "image/webp", "cache-control": "public, max-age=604800" } });
      }
      if (p === "/robots.txt") return new Response("User-agent: *\nAllow: /\nDisallow: /driver\nDisallow: /track/\nDisallow: /thanks\nDisallow: /api/\nSitemap: https://colossalpotato.com/sitemap.xml\n", { headers: { "content-type": "text/plain" } });
      if (p === "/sitemap.xml") return new Response(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://colossalpotato.com/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url><url><loc>https://colossalpotato.com/nutrition</loc><changefreq>monthly</changefreq><priority>0.6</priority></url></urlset>`, { headers: { "content-type": "application/xml" } });
      if (p === "/nutrition") return page(env, "nutrition.html");
      if (p === "/thanks") return page(env, "thanks.html", { "__TOKEN__": (u.searchParams.get("t") || "").replace(/[^a-f0-9]/g, "") });
      if (p.startsWith("/track/")) return page(env, "track.html", { "__TOKEN__": p.slice(7).replace(/[^a-f0-9]/g, "") });
      if (p === "/driver") return page(env, "driver.html");
      if (p === "/" || p === "/index.html") { const h = await env.IMG.get("index.html"); return new Response(h || "Coming soon", { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=120" } }); }
      return Response.redirect(u.origin + "/", 302);
    } catch (e) { return json({ error: "Server error. Please try again." }, 500); }
  }
};
