"""
Startup Financing Platform - ML Recommendation Engine

Version 1:
- Content-based compatibility
- TF-IDF + cosine similarity for profile text
- Explicit compatibility features for industry, stage, investment range, location
- Returns a score from 0 to 100
- Does NOT modify the existing Flask API yet

Later versions can learn weights from real swipe/match data.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_list(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        return [_clean(v) for v in value if _clean(v)]

    text = _clean(value)
    if not text:
        return []

    # Handles simple comma-separated values.
    return [item.strip() for item in text.split(",") if item.strip()]


def _overlap_score(left: Any, right: Any) -> float:
    left_values = set(_to_list(left))
    right_values = set(_to_list(right))

    if not left_values or not right_values:
        return 0.0

    return 1.0 if left_values.intersection(right_values) else 0.0


def _stage_score(startup_stage: Any, preferred_stages: Any) -> float:
    startup = _clean(startup_stage)
    stages = set(_to_list(preferred_stages))

    if not startup or not stages:
        return 0.0

    if startup in stages:
        return 1.0

    # Small normalization for common naming differences.
    aliases = {
        "pre seed": {"pre-seed", "pre_seed"},
        "pre-seed": {"pre seed", "pre_seed"},
        "seed": {"seed stage"},
        "series a": {"series-a", "series_a"},
        "series b": {"series-b", "series_b"},
    }

    for alias in aliases.get(startup, set()):
        if alias in stages:
            return 1.0

    return 0.0


def _investment_score(
    funding_required: Any,
    min_investment: Any,
    max_investment: Any,
) -> float:
    """
    Returns:
      1.0 if requested funding is inside investor range
      0.5 if there is a partial overlap
      0.0 if no useful range information exists / no overlap
    """
    required = _to_float(funding_required)
    minimum = _to_float(min_investment)
    maximum = _to_float(max_investment)

    if required <= 0 or (minimum <= 0 and maximum <= 0):
        return 0.0

    if minimum > 0 and maximum > 0:
        if minimum <= required <= maximum:
            return 1.0

        # Soft score when the request is close to the range.
        distance = minimum - required if required < minimum else required - maximum
        scale = max(required, minimum, maximum, 1.0)
        return max(0.0, 1.0 - (distance / scale))

    if maximum > 0:
        return 1.0 if required <= maximum else max(0.0, maximum / required)

    if minimum > 0:
        return 1.0 if required >= minimum else max(0.0, required / minimum)

    return 0.0


def _build_text(profile: Dict[str, Any], role: str) -> str:
    if role == "PITCHER":
        parts = [
            profile.get("startup_name"),
            profile.get("industry"),
            profile.get("stage"),
            profile.get("description"),
            profile.get("location"),
            profile.get("traction"),
        ]
    else:
        parts = [
            profile.get("investor_name"),
            profile.get("investor_type"),
            profile.get("description"),
            profile.get("location"),
            " ".join(_to_list(profile.get("industries"))),
            " ".join(_to_list(profile.get("preferred_stages"))),
        ]

    return " ".join(_clean(part) for part in parts if _clean(part))


def _text_similarity(pitcher: Dict[str, Any], investor: Dict[str, Any]) -> float:
    documents = [
        _build_text(pitcher, "PITCHER"),
        _build_text(investor, "INVESTOR"),
    ]

    if not any(documents):
        return 0.0

    # With only two documents, fit locally for a deterministic pair score.
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        matrix = vectorizer.fit_transform(documents)
    except ValueError:
        return 0.0

    if matrix.shape[1] == 0:
        return 0.0

    return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])


def compatibility_features(
    pitcher: Dict[str, Any],
    investor: Dict[str, Any],
) -> Dict[str, float]:
    """Return interpretable normalized features in the range 0..1."""

    return {
        "industry_match": _overlap_score(
            pitcher.get("industry"),
            investor.get("industries"),
        ),
        "stage_match": _stage_score(
            pitcher.get("stage"),
            investor.get("preferred_stages"),
        ),
        "investment_fit": _investment_score(
            pitcher.get("funding_required"),
            investor.get("min_investment"),
            investor.get("max_investment"),
        ),
        "location_match": _overlap_score(
            pitcher.get("location"),
            investor.get("location"),
        ),
        "text_similarity": _text_similarity(pitcher, investor),
    }


def compatibility_score(
    pitcher: Dict[str, Any],
    investor: Dict[str, Any],
) -> Tuple[float, Dict[str, float]]:
    """
    Initial interpretable recommendation score.

    These are engineering weights for V1, not learned weights.
    The weights can later be trained from actual user behavior.
    """
    features = compatibility_features(pitcher, investor)

    weights = {
        "industry_match": 0.30,
        "stage_match": 0.20,
        "investment_fit": 0.25,
        "location_match": 0.10,
        "text_similarity": 0.15,
    }

    score = sum(features[name] * weight for name, weight in weights.items())
    return round(score * 100.0, 2), features


def rank_investors(
    pitcher: Dict[str, Any],
    investors: Iterable[Dict[str, Any]],
    top_k: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Rank investor profiles for one pitcher."""

    ranked = []

    for investor in investors:
        score, features = compatibility_score(pitcher, investor)

        result = dict(investor)
        result["compatibility_score"] = score
        result["compatibility_features"] = features
        ranked.append(result)

    ranked.sort(
        key=lambda item: item["compatibility_score"],
        reverse=True,
    )

    if top_k is not None:
        ranked = ranked[:max(0, int(top_k))]

    return ranked


def rank_pitchers(
    investor: Dict[str, Any],
    pitchers: Iterable[Dict[str, Any]],
    top_k: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Rank pitcher profiles for one investor."""

    ranked = []

    for pitcher in pitchers:
        score, features = compatibility_score(pitcher, investor)

        result = dict(pitcher)
        result["compatibility_score"] = score
        result["compatibility_features"] = features
        ranked.append(result)

    ranked.sort(
        key=lambda item: item["compatibility_score"],
        reverse=True,
    )

    if top_k is not None:
        ranked = ranked[:max(0, int(top_k))]

    return ranked
