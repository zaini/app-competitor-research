# App competitor research

A Claude Code skill that researches a mobile app's market and writes a long HTML report. The report covers every competitor with numbers and links, what they likely spend on Meta and Apple Search Ads, their ads, onboarding and pricing, where your app ranks in App Store and Google Play search, an Apple Search Ads plan, review themes, feature ideas, and a prioritised list of what to do next.

Claude does the research in **your own Chrome browser**, mostly on [AppKittie](https://www.appkittie.com), plus the Meta Ad Library and Apple's public review feeds. No API keys needed.

## Install: paste this into Claude Code

```
Install the "app-competitor-research" skill for me: clone https://github.com/zaini/app-competitor-research into ~/.claude/skills/app-competitor-research (if that folder already exists, run git pull in it instead). Then read its SKILL.md and README.md, check that the Claude in Chrome extension is connected, and tell me what I need before I can use it.
```

After installing, restart Claude Code so it picks up the skill.

## Use it

Ask something like:

> Research my app's competitors: https://apps.apple.com/app/id123456789

or type `/app-competitor-research`. Claude asks for:

1. your app's App Store / Google Play link or name
2. competitors you already know (optional)
3. the countries that matter to you
4. your real numbers, such as downloads, revenue and ad spend (optional; they make the estimates more accurate)
5. where to save the report
6. whether it may add favourites and keywords to your AppKittie account

Then it works through your browser for a while (typically 1–3 hours for a thorough report) and saves:

```
<your-folder>/
  <app>-market-research.html   ← open this in a browser
  assets/                      ← screenshots, ad creatives, store images, onboarding screens
  data/                        ← collected numbers, keyword tables, review stats
```

## What you need

- **Claude Code** with the **Claude in Chrome** extension connected, so Claude can drive your browser.
- An **AppKittie account**, logged in in that Chrome. A paid plan unlocks onboarding screens, keyword tools and more data; the free tier gives a thinner report.
- **Python 3**, for the review script (preinstalled on macOS).

## What's in here

| File | What it is |
|---|---|
| `SKILL.md` | The skill itself: the questions to ask first, then the research steps. |
| `references/appkittie-browser-guide.md` | AppKittie's pages, how to read data from them in the browser, and known quirks. |
| `references/estimation-methods.md` | How to estimate competitors' downloads, revenue and ad spend, and how far to trust the numbers. |
| `references/report-outline.md` | The report structure and style. |
| `scripts/fetch_app_store_reviews.py` | Pulls recent App Store reviews from Apple's public feed and counts complaint themes. |

## Good to know

- AppKittie's downloads, revenue and ad-spend figures are **estimates**. The report says how far to trust them, and they're more accurate if you share your own numbers.
- AppKittie mostly sees EU ad libraries, so the skill also checks the Meta Ad Library for US and UK ads.
- Saving lots of AppKittie favourites quickly can make AppKittie return errors. The skill paces itself and lists anything that didn't save.
- Claude only changes your AppKittie favourites, Keyword Explorer and "Your Apps" tracking, and only if you say yes. It never buys anything or touches your ad accounts.

## Manual install

```bash
git clone https://github.com/zaini/app-competitor-research ~/.claude/skills/app-competitor-research
```

To use it in a single project only, clone it into that project's `.claude/skills/` folder instead.
