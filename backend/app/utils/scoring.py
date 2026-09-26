def clamp_score(
    score: float,
    minimum: float = 0.0,
    maximum: float = 1.0,
) -> float:
    return max(
        minimum,
        min(score, maximum),
    )


def weighted_score(
    scores: dict[str, float],
    weights: dict[str, float],
) -> float:
    if not scores:
        return 0.0

    total_weight = sum(
        weights.get(key, 0.0)
        for key in scores
    )

    if total_weight <= 0:
        return 0.0

    score = sum(
        scores[key] * weights.get(key, 0.0)
        for key in scores
    )

    return clamp_score(
        score / total_weight
    )


def percentage(
    score: float,
) -> float:
    return round(
        clamp_score(score) * 100,
        2,
    )