# AppKittie browser guide

Everything here is done in the user's logged-in Chrome via Claude in Chrome. Load the browser tools in one ToolSearch call (`tabs_context_mcp, navigate, computer, read_page, find, get_page_text, javascript_tool, browser_batch, read_network_requests`). Create your own tab; batch actions with `browser_batch`, but keep each batch short (6–8 page loads at most) or it times out.

## Pages

| Page | URL | Use it for |
|---|---|---|
| Explore (app search) | `https://www.appkittie.com/dashboard/explore?search=<query>` | Finding competitors. Filters: store, category, sort by downloads / revenue / growth. |
| App profile | `https://www.appkittie.com/app/<slug>` | Everything about one app (see below). |
| Ads explorer | `https://www.appkittie.com/dashboard/ads` | Search creatives by keyword across apps; sort by newest. |
| Organic | `https://www.appkittie.com/dashboard/organic` and `/dashboard/organic/<slug>` | Creator videos tagged to an app, with views. |
| Onboardings | `https://www.appkittie.com/dashboard/onboarding` | Browse onboarding flows by category; paywalls. |
| Trending / Rising | `/dashboard/trending`, `/dashboard/rising` | Store charts and fast risers. |
| Keyword Explorer | `/dashboard/aso/keywords` | Keyword popularity, difficulty, opportunity, related ideas. |
| Your Apps | `/dashboard/aso/apps` | Keyword positions for the user's own app per store/market. |
| Favourites | `/dashboard/favorites/{apps,ads,apple-ads,onboardings,organic,creators}` | What's been saved. |

Slug formats: iOS `app-<title-words>-id<appstoreid>`, Android `google-play-<package-without-dots>`. Get a slug from the Explore result link.

## App profile anatomy

Header: icon, title, developer, release and last-update dates, category chips, IAP price range, sentiment bar, country chart chips (e.g. "#13" with a flag), and counters: **Est. monthly downloads**, **Est. monthly revenue**, **Active Ads** (Meta), **TikTok Ads**, **Apple Ads**, size, platforms, rating.

Read the counters with one script:

```js
const t=document.body.innerText; const g=re=>{const m=t.match(re);return m?m[1]:'-'};
[document.title.split(' App:')[0], 'apple='+g(/Apple Ads\s*\n?\s*([\d,]+)/), 'meta='+g(/Active Ads\s*\n?\s*([\d,]+)/), 'tiktok='+g(/TikTok Ads\s*\n?\s*([\d,]+)/)].join(' | ')
```

Below the header, a tab bar: All, Overview (downloads / revenue / reviews charts with 1M / 3M / 10M / All ranges), Meta Ads (library of creatives with Videos/Images filters), Ad Spend, TikTok Ads, Ads Funnel, Apple Ads (EU-only creatives, countries, placements, how long it has run), Onboarding (screens labelled Questions / Paywall / Other, paywall position), Reviews, In-app purchases, Contacts, Details. Scroll the page or click a tab, then screenshot.

## Extracting tables

AppKittie tables are normal `<table>` elements. Read rows with:

```js
[...document.querySelectorAll('table tbody tr')].map(tr=>tr.innerText.replace(/\s+/g,' ')).join(' / ')
```

Tool output is truncated around 1,500 characters and some strings are filtered (avoid `=>` in output text). Return big results in slices (`.slice(0,12)`), or store them on `window.__x` and read them in parts. Keep each script under ~40 seconds or the call times out; for slow loops, start an async function that writes to `window.__x` and poll it.

## Your Apps (keyword positions)

1. `/dashboard/aso/apps` → **Add App** → search or paste the store URL → pick the store and markets.
2. The card shows "Analyzing markets…" for 5–20 minutes. Work on something else.
3. When the card shows "N keywords", open it: the table lists the top suggested keywords with **Position** (#1… or "Not ranked"), **Popularity**, **Difficulty**. Switch market with the country dropdown. Extract with the table script above. Screenshot it.

## Keyword Explorer

1. Click the search box ("Search, paste keywords…"), type up to 4 comma-separated keywords, click **Explore**.
2. A dialog asks for the store and markets (US preselected; click others such as GB). Click **Explore N countries**.
3. Each keyword appears in the workspace with "Analyzing…", then a score. Click one to see its overview and **Ideas** (≈20 related keywords with opportunity / popularity / difficulty). Extract with the table script.
4. Batches sometimes fail silently. Check the workspace count afterwards and re-add anything missing.

## Favourites (only if the user agreed)

- **Apps:** on a profile, the header heart button has `title="Save app"`. Clicking it opens a "Save app" dialog with folders (No folder, existing folders, and a "New folder" field) and a **Save app** button. Create a folder named after the user's app the first time.
- **Apple ads:** the card's heart has `title="Save ad"`. **Meta/TikTok creatives:** a text button "Save" under each card. **Onboarding:** `title="Save onboarding"` (its dialog button just says "Save"). Single screens: `title="Save screen"`. **Organic videos:** "Save" under each video card.
- **Use real clicks** (the `computer` tool's `left_click`) for the folder row and the dialog's Save button. Scripted `.click()` calls often look as if they worked but don't persist. You can open the dialog with a script, then take a screenshot to get coordinates.
- **Pace it**: one save every 3–5 seconds, wait ~3 seconds after the last save before leaving the page, and check it persisted (the heart fills, the title becomes "Remove … from favorites", or the favourites page count goes up).
- If saves stop working, read the network log (`read_network_requests`, pattern `favorites`). A 503 on `/api/trpc/favorites.toggle` means AppKittie is refusing saves (rate limit or outage). Wait several minutes or stop, and list what didn't save in the summary.

## What AppKittie can't do (work around it)

- **Ads coverage is mostly EU.** Meta transparency and Apple Ads creatives come from EU ad repositories (UK sometimes). Check the Meta Ad Library website for US, UK and other non-EU ads.
- **Estimates are modelled.** Revenue is often downloads × a round multiplier (×3, ×5, ×15). Downloads for small apps can be ~2× too high. Calibrate with the user's real numbers when you have them.
- **Some markets are missing.** Keyword difficulty and store charts may not support every country (some countries and categories returned nothing in testing). Say so in the report.
- **The creator search can match words, not apps** (e.g. every profile whose name contains a word from the app name). Prefer creators found through organic videos tagged to the app.

## Meta Ad Library (website)

`https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=<CC>&q=<brand or keyword>&search_type=keyword_unordered&media_type=all`

The results header shows "~N results". Click a page name to see all of that page's ads (`view_all_page_id=<id>`). Record active-ad counts, the page name, link titles, start dates, and 2–4 example hooks. Keyword search also matches unrelated brands with the same name, so check the page name.

## App Store review feed (no browser needed)

`https://itunes.apple.com/<cc>/rss/customerreviews/page=<1-10>/id=<appstoreid>/sortby=mostrecent/json` returns 50 recent reviews per page. Use `scripts/fetch_app_store_reviews.py`.
