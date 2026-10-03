HIGH_PRIORITY_KEYWORDS = [
    "fire",
    "accident",
    "emergency",
    "exposed wire",
    "electric wire",
    "open manhole",
    "gas leak",
    "collapsed",
    "dangerous",
    "injury",
    "injured",
    "flooding",
    "major leak",
    "sewage overflow"
]

MEDIUM_PRIORITY_KEYWORDS = [
    "overflowing",
    "blocked",
    "broken",
    "leaking",
    "no water",
    "not working",
    "pothole",
    "garbage",
    "street light",
    "drain"
]


def detect_priority(complaint):
    """Determine complaint priority using keyword-based rules."""

    text = complaint.lower()

    for keyword in HIGH_PRIORITY_KEYWORDS:
        if keyword in text:
            return "High"

    for keyword in MEDIUM_PRIORITY_KEYWORDS:
        if keyword in text:
            return "Medium"

    return "Low"