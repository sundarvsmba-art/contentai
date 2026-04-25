CATEGORY_BASE_SCORES = {
    'tamil_politics': 72,
    'global_news': 65,
    'ai_tech': 62,
    'celebrity': 70,
    'emotional': 75,
}

_VIRAL_KEYWORDS = {
    'breaking': 8, 'exclusive': 7, 'shocking': 8, 'viral': 10, 'exposed': 8,
    'leaked': 9, 'arrested': 7, 'death': 6, 'crisis': 7, 'scandal': 8,
    'wins': 5, 'loses': 5, 'ban': 6, 'attack': 6, 'emergency': 8,
    'record': 5, 'first': 4, 'new': 3, 'revealed': 6, 'secret': 7,
    'unbelievable': 7, 'historic': 6, 'explosive': 8, 'warning': 5,
    'urgent': 7, 'defeat': 5, 'victory': 5, 'protest': 6, 'resign': 7,
}

_NEGATIVE_KEYWORDS = {'routine', 'normal', 'usual', 'regular', 'scheduled'}


def calculate_viral_score(topic: str, category: str) -> int:
    base = CATEGORY_BASE_SCORES.get(category, 50)
    topic_lower = topic.lower()

    bonus = 0
    for kw, weight in _VIRAL_KEYWORDS.items():
        if kw in topic_lower:
            bonus += weight
    for kw in _NEGATIVE_KEYWORDS:
        if kw in topic_lower:
            bonus -= 5

    # Shorter, punchier topics score slightly higher
    words = len(topic.split())
    if words <= 5:
        bonus += 5
    elif words > 15:
        bonus -= 3

    return min(100, max(1, base + bonus))
