import logging
from typing import List, Dict
import requests
import feedparser

logger = logging.getLogger(__name__)

# Google News RSS feeds per category — no API key required
_CATEGORY_FEEDS: Dict[str, List[str]] = {
    'tamil_politics': [
        'https://news.google.com/rss/search?q=Tamil+Nadu+politics&hl=en-IN&gl=IN&ceid=IN:en',
        'https://news.google.com/rss/search?q=Tamil+Nadu+government+2026&hl=en-IN&gl=IN&ceid=IN:en',
    ],
    'global_news': [
        'https://feeds.bbci.co.uk/news/world/rss.xml',
        'https://news.google.com/rss/headlines/section/geo/IN?hl=en-IN&gl=IN&ceid=IN:en',
    ],
    'ai_tech': [
        'https://news.google.com/rss/search?q=artificial+intelligence+2026&hl=en&gl=US&ceid=US:en',
        'https://news.google.com/rss/search?q=technology+India+startup+2026&hl=en-IN&gl=IN&ceid=IN:en',
    ],
    'celebrity': [
        'https://news.google.com/rss/search?q=Bollywood+celebrity+news&hl=en-IN&gl=IN&ceid=IN:en',
        'https://news.google.com/rss/search?q=Tamil+actor+kollywood+news&hl=en-IN&gl=IN&ceid=IN:en',
    ],
    'emotional': [
        'https://news.google.com/rss/search?q=inspirational+story+India&hl=en-IN&gl=IN&ceid=IN:en',
        'https://news.google.com/rss/search?q=viral+emotional+story+India&hl=en-IN&gl=IN&ceid=IN:en',
    ],
}

_HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; TrendBot/1.0)'}


def _fetch_rss(url: str, max_items: int = 6) -> List[str]:
    try:
        resp = requests.get(url, timeout=10, headers=_HEADERS)
        resp.raise_for_status()
        feed = feedparser.parse(resp.content)
        titles = []
        for entry in feed.entries[:max_items]:
            title = (entry.get('title') or '').strip()
            # Strip source suffix like " - BBC News"
            if ' - ' in title:
                title = title.rsplit(' - ', 1)[0].strip()
            if title and len(title) > 5:
                titles.append(title)
        return titles
    except Exception as exc:
        logger.warning("RSS fetch failed for %s: %s", url, exc)
        return []


def _fetch_google_trends() -> List[Dict]:
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl='en-IN', tz=330, timeout=(5, 15))
        df = pt.trending_searches(pn='india')
        topics = df[0].dropna().tolist()[:12]
        return [
            {'topic': str(t).strip(), 'source': 'google_trends', 'category': 'global_news'}
            for t in topics if str(t).strip()
        ]
    except Exception as exc:
        logger.warning("Google Trends fetch failed: %s", exc)
        return []


def fetch_all_trends() -> List[Dict]:
    """Return list of {topic, source, category} dicts from all sources."""
    results: List[Dict] = []

    for category, feeds in _CATEGORY_FEEDS.items():
        for url in feeds:
            for title in _fetch_rss(url):
                results.append({'topic': title, 'source': 'rss', 'category': category})

    results.extend(_fetch_google_trends())

    # Deduplicate by normalised topic
    seen: set = set()
    unique: List[Dict] = []
    for item in results:
        key = item['topic'].lower()[:100]
        if key not in seen:
            seen.add(key)
            unique.append(item)

    logger.info("fetch_all_trends: %s unique topics collected", len(unique))
    return unique
