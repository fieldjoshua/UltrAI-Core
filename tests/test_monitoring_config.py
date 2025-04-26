import pytest
import os
import yaml
from pathlib import Path


def test_prometheus_config():
    # Test Prometheus configuration
    prometheus_dir = Path("monitoring/prometheus")
    assert prometheus_dir.exists()

    # Test prometheus.yml
    prometheus_path = prometheus_dir / "prometheus.yml"
    assert prometheus_path.exists()

    with open(prometheus_path, "r") as f:
        prometheus = yaml.safe_load(f)

        # Verify Prometheus configuration
        assert "global" in prometheus
        assert "scrape_configs" in prometheus

        # Verify global settings
        global_config = prometheus["global"]
        assert "scrape_interval" in global_config
        assert "evaluation_interval" in global_config

        # Verify scrape configs
        scrape_configs = prometheus["scrape_configs"]
        assert len(scrape_configs) > 0
        for config in scrape_configs:
            assert "job_name" in config
            assert "static_configs" in config


def test_grafana_config():
    # Test Grafana configuration
    grafana_dir = Path("monitoring/grafana")
    assert grafana_dir.exists()

    # Test datasources
    datasources_path = grafana_dir / "datasources.yaml"
    assert datasources_path.exists()

    with open(datasources_path, "r") as f:
        datasources = yaml.safe_load(f)

        # Verify datasources configuration
        assert "apiVersion" in datasources
        assert "datasources" in datasources

        # Verify Prometheus datasource
        prometheus_ds = next(
            ds for ds in datasources["datasources"] if ds["name"] == "Prometheus"
        )
        assert prometheus_ds["type"] == "prometheus"
        assert prometheus_ds["url"] == "http://prometheus:9090"
        assert prometheus_ds["access"] == "proxy"


def test_alertmanager_config():
    # Test Alertmanager configuration
    alertmanager_dir = Path("monitoring/alertmanager")
    assert alertmanager_dir.exists()

    # Test alertmanager.yml
    alertmanager_path = alertmanager_dir / "alertmanager.yml"
    assert alertmanager_path.exists()

    with open(alertmanager_path, "r") as f:
        alertmanager = yaml.safe_load(f)

        # Verify Alertmanager configuration
        assert "global" in alertmanager
        assert "route" in alertmanager
        assert "receivers" in alertmanager

        # Verify global settings
        global_config = alertmanager["global"]
        assert "resolve_timeout" in global_config

        # Verify route configuration
        route = alertmanager["route"]
        assert "group_by" in route
        assert "receiver" in route
        assert "routes" in route


def test_node_exporter_config():
    # Test Node Exporter configuration
    node_exporter_dir = Path("monitoring/node-exporter")
    assert node_exporter_dir.exists()

    # Test node-exporter.yml
    node_exporter_path = node_exporter_dir / "node-exporter.yml"
    assert node_exporter_path.exists()

    with open(node_exporter_path, "r") as f:
        node_exporter = yaml.safe_load(f)

        # Verify Node Exporter configuration
        assert "collectors" in node_exporter
        assert "collectors.diskstats" in node_exporter
        assert "collectors.filesystem" in node_exporter
        assert "collectors.meminfo" in node_exporter
        assert "collectors.netdev" in node_exporter


def test_kube_state_metrics_config():
    # Test kube-state-metrics configuration
    ksm_dir = Path("monitoring/kube-state-metrics")
    assert ksm_dir.exists()

    # Test kube-state-metrics.yml
    ksm_path = ksm_dir / "kube-state-metrics.yml"
    assert ksm_path.exists()

    with open(ksm_path, "r") as f:
        ksm = yaml.safe_load(f)

        # Verify kube-state-metrics configuration
        assert "metricLabelsAllowlist" in ksm
        assert "metricAnnotationsAllowList" in ksm

        # Verify metric labels
        labels = ksm["metricLabelsAllowlist"]
        assert "pods" in labels
        assert "nodes" in labels
        assert "services" in labels


def test_custom_metrics_config():
    # Test custom metrics configuration
    custom_metrics_dir = Path("monitoring/custom-metrics")
    assert custom_metrics_dir.exists()

    # Test custom-metrics.yml
    custom_metrics_path = custom_metrics_dir / "custom-metrics.yml"
    assert custom_metrics_path.exists()

    with open(custom_metrics_path, "r") as f:
        custom_metrics = yaml.safe_load(f)

        # Verify custom metrics configuration
        assert "rules" in custom_metrics
        assert "groups" in custom_metrics

        # Verify rules
        rules = custom_metrics["groups"]
        assert len(rules) > 0
        for group in rules:
            assert "name" in group
            assert "rules" in group


def test_dashboard_config():
    # Test dashboard configuration
    dashboard_dir = Path("monitoring/dashboards")
    assert dashboard_dir.exists()

    # Test dashboard.json
    dashboard_path = dashboard_dir / "dashboard.json"
    assert dashboard_path.exists()

    with open(dashboard_path, "r") as f:
        dashboard = yaml.safe_load(f)

        # Verify dashboard configuration
        assert "dashboard" in dashboard
        assert "panels" in dashboard["dashboard"]

        # Verify panels
        panels = dashboard["dashboard"]["panels"]
        assert len(panels) > 0
        for panel in panels:
            assert "title" in panel
            assert "type" in panel
            assert "datasource" in panel
