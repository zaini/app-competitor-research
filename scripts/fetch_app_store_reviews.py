#!/usr/bin/env python3
"""Fetch recent App Store reviews from Apple's public RSS feed and tag them by theme.

Usage:
  python3 fetch_app_store_reviews.py OUT_DIR APP_ID[:Name] [APP_ID[:Name] ...] [--countries us,gb] [--pages 5]

APP_ID is the numeric App Store id (the digits after "id" in the store URL).
Writes OUT_DIR/reviews/<id>.json per app and OUT_DIR/review_stats.json with averages,
1-2 star counts and theme counts. Edit THEMES to fit the app's category.
No login or API key needed.
"""
import json, os, re, sys, urllib.request

THEMES = {
    'price/subscription': r'price|expensive|subscri|pay|paywall|money|cost|free trial|trial|charged|refund|scam|cancel',
    'ads': r'\bads?\b|advert',
    'bugs/crash': r"crash|bug|glitch|freez|doesn.t work|not working|broken|stuck|loading",
    'audio/voice': r'audio|pronunc|voice|sound|accent|listen|speak',
    'content depth': r'more (lessons|content|levels)|limited|repetit|too easy|basic|run out|finished',
    'AI': r'\bai\b|chatgpt|chat bot|chatbot',
    'kids': r'kid|child|son|daughter|toddler|year old',
    'devices': r'ipad|tablet|android|offline',
    'support/account': r'support|login|log in|account|sign in|email',
    'praise': r'love|great|amazing|best|excellent|fun|helpful|perfect',
}


def fetch(app_id, cc, page):
    url = f'https://itunes.apple.com/{cc}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json'
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            js = json.load(r)
    except Exception:
        return []
    entries = js.get('feed', {}).get('entry', [])
    if isinstance(entries, dict):
        entries = [entries]
    out = []
    for e in entries:
        if 'im:rating' not in e:
            continue
        out.append(dict(rating=int(e['im:rating']['label']), title=e['title']['label'], body=e['content']['label'],
                        date=e['updated']['label'][:10], version=e.get('im:version', {}).get('label'), cc=cc))
    return out


def main():
    args = sys.argv[1:]
    countries, pages = ['us', 'gb'], 5
    if '--countries' in args:
        i = args.index('--countries'); countries = args[i + 1].split(','); del args[i:i + 2]
    if '--pages' in args:
        i = args.index('--pages'); pages = int(args[i + 1]); del args[i:i + 2]
    out_dir, apps = args[0], args[1:]
    os.makedirs(f'{out_dir}/reviews', exist_ok=True)
    stats = {}
    for spec in apps:
        app_id, _, name = spec.partition(':')
        reviews = []
        for cc in countries:
            for p in range(1, pages + 1):
                batch = fetch(app_id, cc, p)
                reviews += batch
                if len(batch) < 50:
                    break
        json.dump(dict(app_id=app_id, name=name, reviews=reviews), open(f'{out_dir}/reviews/{app_id}.json', 'w'), ensure_ascii=False, indent=0)
        if not reviews:
            print(f'{name or app_id}: no reviews'); continue
        neg = [r for r in reviews if r['rating'] <= 2]
        text = lambda r: r['title'] + ' ' + r['body']
        themes = {k: dict(all=sum(1 for r in reviews if re.search(p, text(r), re.I)), negative=sum(1 for r in neg if re.search(p, text(r), re.I))) for k, p in THEMES.items()}
        avg = sum(r['rating'] for r in reviews) / len(reviews)
        stats[app_id] = dict(name=name, n=len(reviews), avg=round(avg, 2), negative=len(neg), latest=max(r['date'] for r in reviews), themes=themes)
        top = sorted(themes.items(), key=lambda kv: -kv[1]['negative'])[:3]
        print(f"{name or app_id}: {len(reviews)} reviews, avg {avg:.2f}, {len(neg)} rated 1-2; top complaints: " + ', '.join(f"{k} {v['negative']}" for k, v in top))
    json.dump(stats, open(f'{out_dir}/review_stats.json', 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
