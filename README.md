# Colossal Potato — Meal Prep Ordering Platform

**Live site:** [colossalpotato.com](https://colossalpotato.com) · a BnX Kitchens LLC brand · Sacramento, CA

A complete ordering platform built for a local meal-prep business that sells high-protein loaded potato bowls in 5-packs. It runs serverless on Cloudflare Workers. It handles the menu, delivery scheduling, distance-based fees, Stripe checkout, SMS updates, live driver tracking, and an animated voice mascot that suggests add-ons.

## Features

| Area | What it does |
|---|---|
| **Menu & cart** | 8 bowls, add-ons, sauce options, and a low-carb cauliflower swap. Everything is sold in 5-packs. |
| **Scheduling** | Three delivery windows with order cutoffs (7 PM night before → 9–11 AM, 11 AM → 2–4 PM, 3 PM → 7–9 PM). Preorders up to 3 months ahead. Daily and per-window capacity caps. |
| **Delivery pricing** | Geocodes the address (OpenStreetMap Nominatim) and gets the driving distance (OSRM). $7 up to 10 mi, $14 up to 20 mi, one fee per order. |
| **Checkout** | Stripe Checkout, with orders held for 20 minutes while the customer pays. A signed Stripe webhook confirms each payment. |
| **Order tracking** | Each customer gets a private tracking page with prep → cook → out-for-delivery stages and a live driver map with an ETA. |
| **Driver app** | Mobile web app that orders the stops, marks each delivery, and sends stage updates by SMS (Twilio). |
| **Spud mascot** | Animated SVG mascot in the header with 25+ moves and emotions, voice lines with lip-sync driven by the Web Audio API, idle behaviors, and bowl-aware upsells (e.g. suggests extra steak on the Steakhouse bowl, or a breakfast pack if the cart has none). |
| **Nutrition** | `/nutrition` page with FDA-style Nutrition Facts labels, calculated from USDA FoodData Central values for standard portions. |
| **Local SEO** | Title and meta tags, FoodEstablishment and FAQPage structured data, service-area cities, Open Graph tags, `robots.txt`, and `sitemap.xml`. |

## Stack

- **Cloudflare Workers** for routing, the API, and pricing logic (`site/worker.js`)
- **Cloudflare D1** (SQLite) for orders and driver state
- **Cloudflare KV** for pages, images, and the voice pack
- **Stripe Checkout + webhooks**, **Twilio SMS**
- **ElevenLabs** for voice generation and transcription (offline asset pipeline)
- **Python** (Pillow, ReportLab, NumPy, FFmpeg) for the printable menu and IG menu, and for rendering the frame-by-frame lip-synced promo videos

## Repo layout

```
site/    Worker + all pages (menu, thanks, tracking, driver, nutrition) and the mascot module
menu/    PDF and Instagram menu generators (ReportLab)
video/   Promo video renderer: PIL frame compositing, RMS-envelope lip-sync, FFmpeg encode, ad-size exports (4:5, 1:1, 16:9)
```

## Notes

- Every secret (Stripe, Twilio, driver code, upload key, kitchen coordinates) is a Cloudflare secret, never in code. The kitchen location stays private, and the live driver map hides the car until it is 0.4 mi away from the kitchen.
- Nutrition values are estimates and are labeled that way on the site.

© 2026 Colossal Potato · BnX Kitchens LLC
