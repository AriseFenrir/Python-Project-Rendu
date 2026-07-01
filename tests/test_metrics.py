from api.metrics import get_system_metrics


def test_metrics_returns_all_fields():
    metrics = get_system_metrics()
    assert "cpu_percent" in metrics
    assert "memory_percent" in metrics
    assert "disk_percent" in metrics


def test_metrics_cpu_in_range():
    metrics = get_system_metrics()
    assert 0 <= metrics["cpu_percent"] <= 100


def test_metrics_memory_in_range():
    metrics = get_system_metrics()
    assert 0 <= metrics["memory_percent"] <= 100


def test_metrics_disk_in_range():
    metrics = get_system_metrics()
    assert 0 <= metrics["disk_percent"] <= 100


def test_metrics_returns_dict():
    metrics = get_system_metrics()
    assert isinstance(metrics, dict)


def test_metrics_values_are_numeric():
    metrics = get_system_metrics()
    assert isinstance(metrics["cpu_percent"], (int, float))
    assert isinstance(metrics["memory_percent"], (int, float))
    assert isinstance(metrics["disk_percent"], (int, float))
