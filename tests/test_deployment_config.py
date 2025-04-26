import pytest
import os
import yaml
from pathlib import Path


def test_kubernetes_config():
    # Test Kubernetes configuration
    k8s_dir = Path("k8s")
    assert k8s_dir.exists()

    # Test deployment
    deploy_path = k8s_dir / "deployment.yaml"
    assert deploy_path.exists()

    with open(deploy_path, "r") as f:
        deploy = yaml.safe_load(f)

        # Verify deployment configuration
        assert deploy["apiVersion"] == "apps/v1"
        assert deploy["kind"] == "Deployment"
        assert "metadata" in deploy
        assert "spec" in deploy

        # Verify container configuration
        containers = deploy["spec"]["template"]["spec"]["containers"]
        assert len(containers) > 0
        container = containers[0]
        assert "name" in container
        assert "image" in container
        assert "ports" in container
        assert "env" in container
        assert "resources" in container


def test_service_config():
    # Test service configuration
    k8s_dir = Path("k8s")
    service_path = k8s_dir / "service.yaml"
    assert service_path.exists()

    with open(service_path, "r") as f:
        service = yaml.safe_load(f)

        # Verify service configuration
        assert service["apiVersion"] == "v1"
        assert service["kind"] == "Service"
        assert "metadata" in service
        assert "spec" in service

        # Verify service spec
        spec = service["spec"]
        assert "type" in spec
        assert "ports" in spec
        assert "selector" in spec


def test_ingress_config():
    # Test ingress configuration
    k8s_dir = Path("k8s")
    ingress_path = k8s_dir / "ingress.yaml"
    assert ingress_path.exists()

    with open(ingress_path, "r") as f:
        ingress = yaml.safe_load(f)

        # Verify ingress configuration
        assert ingress["apiVersion"] == "networking.k8s.io/v1"
        assert ingress["kind"] == "Ingress"
        assert "metadata" in ingress
        assert "spec" in ingress

        # Verify ingress spec
        spec = ingress["spec"]
        assert "rules" in spec
        assert "tls" in spec


def test_configmap():
    # Test ConfigMap
    k8s_dir = Path("k8s")
    configmap_path = k8s_dir / "configmap.yaml"
    assert configmap_path.exists()

    with open(configmap_path, "r") as f:
        configmap = yaml.safe_load(f)

        # Verify ConfigMap configuration
        assert configmap["apiVersion"] == "v1"
        assert configmap["kind"] == "ConfigMap"
        assert "metadata" in configmap
        assert "data" in configmap

        # Verify ConfigMap data
        data = configmap["data"]
        assert "API_KEY" in data
        assert "DATABASE_URL" in data
        assert "LOG_LEVEL" in data


def test_secret():
    # Test Secret
    k8s_dir = Path("k8s")
    secret_path = k8s_dir / "secret.yaml"
    assert secret_path.exists()

    with open(secret_path, "r") as f:
        secret = yaml.safe_load(f)

        # Verify Secret configuration
        assert secret["apiVersion"] == "v1"
        assert secret["kind"] == "Secret"
        assert "metadata" in secret
        assert "data" in secret

        # Verify Secret data
        data = secret["data"]
        assert "API_KEY" in data
        assert "DATABASE_URL" in data
        assert "JWT_SECRET" in data


def test_persistent_volume():
    # Test PersistentVolume
    k8s_dir = Path("k8s")
    pv_path = k8s_dir / "persistent-volume.yaml"
    assert pv_path.exists()

    with open(pv_path, "r") as f:
        pv = yaml.safe_load(f)

        # Verify PV configuration
        assert pv["apiVersion"] == "v1"
        assert pv["kind"] == "PersistentVolume"
        assert "metadata" in pv
        assert "spec" in pv

        # Verify PV spec
        spec = pv["spec"]
        assert "capacity" in spec
        assert "accessModes" in spec
        assert "hostPath" in spec


def test_persistent_volume_claim():
    # Test PersistentVolumeClaim
    k8s_dir = Path("k8s")
    pvc_path = k8s_dir / "persistent-volume-claim.yaml"
    assert pvc_path.exists()

    with open(pvc_path, "r") as f:
        pvc = yaml.safe_load(f)

        # Verify PVC configuration
        assert pvc["apiVersion"] == "v1"
        assert pvc["kind"] == "PersistentVolumeClaim"
        assert "metadata" in pvc
        assert "spec" in pvc

        # Verify PVC spec
        spec = pvc["spec"]
        assert "accessModes" in spec
        assert "resources" in spec


def test_horizontal_pod_autoscaler():
    # Test HorizontalPodAutoscaler
    k8s_dir = Path("k8s")
    hpa_path = k8s_dir / "horizontal-pod-autoscaler.yaml"
    assert hpa_path.exists()

    with open(hpa_path, "r") as f:
        hpa = yaml.safe_load(f)

        # Verify HPA configuration
        assert hpa["apiVersion"] == "autoscaling/v2"
        assert hpa["kind"] == "HorizontalPodAutoscaler"
        assert "metadata" in hpa
        assert "spec" in hpa

        # Verify HPA spec
        spec = hpa["spec"]
        assert "scaleTargetRef" in spec
        assert "minReplicas" in spec
        assert "maxReplicas" in spec
        assert "metrics" in spec
