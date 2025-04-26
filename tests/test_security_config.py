import pytest
import os
import yaml
from pathlib import Path


def test_network_policy():
    # Test network policy
    k8s_dir = Path("k8s")
    network_policy_path = k8s_dir / "network-policy.yaml"
    assert network_policy_path.exists()

    with open(network_policy_path, "r") as f:
        network_policy = yaml.safe_load(f)

        # Verify network policy configuration
        assert network_policy["apiVersion"] == "networking.k8s.io/v1"
        assert network_policy["kind"] == "NetworkPolicy"
        assert "metadata" in network_policy
        assert "spec" in network_policy

        # Verify policy spec
        spec = network_policy["spec"]
        assert "podSelector" in spec
        assert "policyTypes" in spec
        assert "ingress" in spec
        assert "egress" in spec


def test_pod_security_policy():
    # Test pod security policy
    k8s_dir = Path("k8s")
    psp_path = k8s_dir / "pod-security-policy.yaml"
    assert psp_path.exists()

    with open(psp_path, "r") as f:
        psp = yaml.safe_load(f)

        # Verify pod security policy configuration
        assert psp["apiVersion"] == "policy/v1beta1"
        assert psp["kind"] == "PodSecurityPolicy"
        assert "metadata" in psp
        assert "spec" in psp

        # Verify policy spec
        spec = psp["spec"]
        assert "privileged" in spec
        assert "seLinux" in spec
        assert "runAsUser" in spec
        assert "fsGroup" in spec


def test_rbac_config():
    # Test RBAC configuration
    k8s_dir = Path("k8s")
    rbac_dir = k8s_dir / "rbac"
    assert rbac_dir.exists()

    # Test service account
    sa_path = rbac_dir / "service-account.yaml"
    assert sa_path.exists()

    with open(sa_path, "r") as f:
        sa = yaml.safe_load(f)

        # Verify service account configuration
        assert sa["apiVersion"] == "v1"
        assert sa["kind"] == "ServiceAccount"
        assert "metadata" in sa
        assert "name" in sa["metadata"]

    # Test role
    role_path = rbac_dir / "role.yaml"
    assert role_path.exists()

    with open(role_path, "r") as f:
        role = yaml.safe_load(f)

        # Verify role configuration
        assert role["apiVersion"] == "rbac.authorization.k8s.io/v1"
        assert role["kind"] == "Role"
        assert "metadata" in role
        assert "rules" in role

        # Verify rules
        rules = role["rules"]
        assert len(rules) > 0
        for rule in rules:
            assert "apiGroups" in rule
            assert "resources" in rule
            assert "verbs" in rule

    # Test role binding
    rb_path = rbac_dir / "role-binding.yaml"
    assert rb_path.exists()

    with open(rb_path, "r") as f:
        rb = yaml.safe_load(f)

        # Verify role binding configuration
        assert rb["apiVersion"] == "rbac.authorization.k8s.io/v1"
        assert rb["kind"] == "RoleBinding"
        assert "metadata" in rb
        assert "roleRef" in rb
        assert "subjects" in rb


def test_security_context():
    # Test security context
    k8s_dir = Path("k8s")
    deploy_path = k8s_dir / "deployment.yaml"
    assert deploy_path.exists()

    with open(deploy_path, "r") as f:
        deploy = yaml.safe_load(f)

        # Verify security context
        containers = deploy["spec"]["template"]["spec"]["containers"]
        for container in containers:
            assert "securityContext" in container
            sc = container["securityContext"]
            assert "runAsNonRoot" in sc
            assert "readOnlyRootFilesystem" in sc
            assert "capabilities" in sc


def test_network_security():
    # Test network security
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

        # Verify ports
        ports = spec["ports"]
        for port in ports:
            assert "port" in port
            assert "targetPort" in port
            assert "protocol" in port


def test_secret_management():
    # Test secret management
    k8s_dir = Path("k8s")
    secret_path = k8s_dir / "secret.yaml"
    assert secret_path.exists()

    with open(secret_path, "r") as f:
        secret = yaml.safe_load(f)

        # Verify secret configuration
        assert secret["apiVersion"] == "v1"
        assert secret["kind"] == "Secret"
        assert "metadata" in secret
        assert "data" in secret

        # Verify secret data
        data = secret["data"]
        assert "API_KEY" in data
        assert "DATABASE_URL" in data
        assert "JWT_SECRET" in data

        # Verify secret is base64 encoded
        for value in data.values():
            assert value.isalnum()  # Base64 encoded strings are alphanumeric
