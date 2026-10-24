"""Unit tests for the entropy engine math."""

import pytest
from backend import entropy_engine as ee


def test_decay_stage_boundaries():
    assert ee.get_decay_stage(0.0) == 1
    assert ee.get_decay_stage(0.19) == 1
    assert ee.get_decay_stage(0.20) == 2
    assert ee.get_decay_stage(0.44) == 2
    assert ee.get_decay_stage(0.45) == 3
    assert ee.get_decay_stage(0.69) == 3
    assert ee.get_decay_stage(0.70) == 4
    assert ee.get_decay_stage(0.89) == 4
    assert ee.get_decay_stage(0.90) == 5
    assert ee.get_decay_stage(1.0) == 5


def test_decay_never_exceeds_one():
    for _ in range(100):
        result = ee.calculate_decay(0.95, 0.015, 100, demo_mode=True)
        assert result <= 1.0


def test_decay_increases():
    # Over many samples, decay on average increases entropy
    total = 0.0
    for _ in range(50):
        total += ee.calculate_decay(0.5, 0.01, 10) - 0.5
    assert total > 0  # average positive


def test_maintenance_rollback_decreases_with_entropy():
    low = ee.calculate_maintenance_rollback(0.1)
    high = ee.calculate_maintenance_rollback(0.95)
    assert low > high
    assert high < 0.001  # near-useless at high entropy
    assert low > 0.03    # meaningful at low entropy


def test_condole_effect_capped():
    # Fresh monument: full per-condole effect
    assert ee.calculate_condole_effect(0.0) == 0.03
    # Near cap: only remaining allowed
    assert ee.calculate_condole_effect(0.14) == pytest.approx(0.01)
    # Over cap: zero
    assert ee.calculate_condole_effect(0.15) == 0.0
    assert ee.calculate_condole_effect(0.20) == 0.0


def test_cert_decay_rate_is_triple():
    # Cert decay rate = average of type range × 3
    rate = ee.get_cert_decay_rate("relic")
    expected = (0.003 + 0.010) / 2 * 3
    assert rate == pytest.approx(expected, abs=1e-6)


def test_assign_decay_rate_in_range():
    for mtype, (low, high) in ee.BASE_DECAY_RATES.items():
        for _ in range(20):
            rate = ee.assign_decay_rate(mtype)
            assert low <= rate <= high


def test_tilt_angle_deterministic():
    # Same seed → same direction always
    a = ee.tilt_angle(100, 0.5)
    b = ee.tilt_angle(100, 0.5)
    assert a == b
