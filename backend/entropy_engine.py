"""
Entropy Engine — the mathematical heart of 熵逝碑林.

Implements:
- Decay rate assignment (randomized per monument type)
- Entropy score calculation (with random noise)
- Decay stage thresholds
- Maintenance rollback formula
- Condolence effect
"""

import random

# Decay rate ranges (per real-world hour) for each monument type
BASE_DECAY_RATES: dict[str, tuple[float, float]] = {
    "code":     (0.005, 0.012),
    "relic":    (0.003, 0.010),
    "link":     (0.008, 0.015),
    "nameless": (0.004, 0.011),
}

# Stage thresholds
STAGE_THRESHOLDS = [0.0, 0.20, 0.45, 0.70, 0.90, 1.0]
STAGE_NAMES = ["崭新期", "风化期", "锈蚀期", "废墟期", "寂灭期"]

# Demo mode speed multiplier (30 real days → ~1 hour)
DEMO_MULTIPLIER = 720.0


def assign_decay_rate(monument_type: str) -> float:
    """
    Assign a randomized decay rate for a new monument.
    Returns a float representing entropy increase per real hour.
    """
    low, high = BASE_DECAY_RATES.get(monument_type, (0.004, 0.010))
    return round(random.uniform(low, high), 6)


def calculate_decay(
    entropy_score: float,
    decay_rate: float,
    elapsed_hours: float,
    demo_mode: bool = False,
) -> float:
    """
    Calculate new entropy score after elapsed_hours.
    Includes random noise in [-0.1, +0.2] to make decay feel organic.
    """
    multiplier = DEMO_MULTIPLIER if demo_mode else 1.0
    noise = random.uniform(-0.1, 0.2)
    delta = decay_rate * elapsed_hours * multiplier * (1.0 + noise)
    return min(1.0, entropy_score + max(0.0, delta))  # delta can't go negative


def get_decay_stage(entropy_score: float) -> int:
    """
    Returns the decay stage (1–5) for a given entropy score.
    Stage 1: 崭新期 (0.0–0.20)
    Stage 2: 风化期 (0.20–0.45)
    Stage 3: 锈蚀期 (0.45–0.70)
    Stage 4: 废墟期 (0.70–0.90)
    Stage 5: 寂灭期 (0.90–1.0)
    """
    if entropy_score < 0.20:
        return 1
    if entropy_score < 0.45:
        return 2
    if entropy_score < 0.70:
        return 3
    if entropy_score < 0.90:
        return 4
    return 5


def get_stage_name(stage: int) -> str:
    """Returns the Chinese name for a decay stage."""
    return STAGE_NAMES[stage - 1] if 1 <= stage <= 5 else "未知"


def calculate_maintenance_rollback(entropy_score: float) -> float:
    """
    Maintenance effect decreases as entropy grows.
    rollback = 0.05 * (1 - entropy_score)^2
    At entropy=0.1: rollback ≈ 0.0405  (meaningful)
    At entropy=0.95: rollback ≈ 0.000125 (barely anything)
    """
    rollback = 0.05 * (1.0 - entropy_score) ** 2
    return round(rollback, 6)


def calculate_condole_effect(
    current_total_condole: float,
    max_condole: float = 0.15,
    per_condole: float = 0.03,
) -> float:
    """
    Calculate how much a condolence action can delay entropy.
    Total condole effect is capped at 0.15 per monument lifetime.
    """
    remaining = max_condole - current_total_condole
    return round(min(per_condole, max(0.0, remaining)), 6)


def get_cert_decay_rate(monument_type: str) -> float:
    """
    Extinction certificates decay 3× faster than normal monuments.
    Uses the average of the monument type's range × 3.
    """
    low, high = BASE_DECAY_RATES.get(monument_type, (0.004, 0.010))
    avg = (low + high) / 2.0
    return round(avg * 3.0, 6)


def tilt_angle(random_seed: int, entropy_score: float) -> float:
    """
    Deterministic tilt angle for a monument based on its random_seed.
    Returns degrees. Sign is consistent per monument; magnitude grows with entropy.
    """
    direction = 1 if (random_seed % 2 == 0) else -1
    magnitude = (random_seed % 7 + 1) * entropy_score  # 1–7 degrees max
    return round(direction * magnitude, 2)
