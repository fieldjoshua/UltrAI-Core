import pytest
from src.models import QualityMetrics


@pytest.fixture
def sample_metrics():
    return QualityMetrics(
        coherence_score=0.8, technical_depth=0.9, strategic_value=0.85, uniqueness=0.75
    )


def test_quality_metrics_initialization():
    metrics = QualityMetrics()
    assert metrics.coherence_score == 0.0
    assert metrics.technical_depth == 0.0
    assert metrics.strategic_value == 0.0
    assert metrics.uniqueness == 0.0


def test_quality_metrics_custom_values(sample_metrics):
    assert sample_metrics.coherence_score == 0.8
    assert sample_metrics.technical_depth == 0.9
    assert sample_metrics.strategic_value == 0.85
    assert sample_metrics.uniqueness == 0.75


def test_quality_metrics_average_score(sample_metrics):
    expected_average = (0.8 + 0.9 + 0.85 + 0.75) / 4
    assert sample_metrics.average_score() == expected_average


def test_quality_metrics_zero_scores():
    metrics = QualityMetrics(
        coherence_score=0.0, technical_depth=0.0, strategic_value=0.0, uniqueness=0.0
    )
    assert metrics.average_score() == 0.0


def test_quality_metrics_max_scores():
    metrics = QualityMetrics(
        coherence_score=1.0, technical_depth=1.0, strategic_value=1.0, uniqueness=1.0
    )
    assert metrics.average_score() == 1.0


def test_quality_metrics_mixed_scores():
    metrics = QualityMetrics(
        coherence_score=0.5, technical_depth=0.7, strategic_value=0.3, uniqueness=0.9
    )
    expected_average = (0.5 + 0.7 + 0.3 + 0.9) / 4
    assert metrics.average_score() == expected_average


def test_quality_metrics_score_validation():
    with pytest.raises(ValueError):
        QualityMetrics(coherence_score=1.5)  # Score > 1.0

    with pytest.raises(ValueError):
        QualityMetrics(technical_depth=-0.1)  # Score < 0.0
