import pytest
import os
import yaml
from pathlib import Path


def test_deployment_script():
    # Test deployment script
    scripts_dir = Path("scripts")
    assert scripts_dir.exists()

    # Test deploy script
    deploy_script = scripts_dir / "deploy.sh"
    assert deploy_script.exists()
    assert os.access(deploy_script, os.X_OK)

    with open(deploy_script, "r") as f:
        content = f.read()

        # Verify deployment commands
        assert "kubectl apply" in content
        assert "kubectl rollout" in content
        assert "kubectl get" in content

        # Verify deployment paths
        assert "k8s/" in content
        assert "config/" in content
        assert "secrets/" in content


def test_setup_script():
    # Test setup script
    scripts_dir = Path("scripts")

    # Test setup script
    setup_script = scripts_dir / "setup.sh"
    assert setup_script.exists()
    assert os.access(setup_script, os.X_OK)

    with open(setup_script, "r") as f:
        content = f.read()

        # Verify setup commands
        assert "python -m venv" in content
        assert "pip install" in content
        assert "cp .env.example" in content

        # Verify setup paths
        assert ".venv" in content
        assert "requirements.txt" in content
        assert ".env" in content


def test_migration_script():
    # Test migration script
    scripts_dir = Path("scripts")

    # Test migration script
    migrate_script = scripts_dir / "migrate.sh"
    assert migrate_script.exists()
    assert os.access(migrate_script, os.X_OK)

    with open(migrate_script, "r") as f:
        content = f.read()

        # Verify migration commands
        assert "alembic upgrade" in content
        assert "alembic revision" in content
        assert "alembic current" in content

        # Verify migration paths
        assert "migrations/" in content
        assert "alembic.ini" in content


def test_backup_script():
    # Test backup script
    scripts_dir = Path("scripts")

    # Test backup script
    backup_script = scripts_dir / "backup.sh"
    assert backup_script.exists()
    assert os.access(backup_script, os.X_OK)

    with open(backup_script, "r") as f:
        content = f.read()

        # Verify backup commands
        assert "pg_dump" in content
        assert "tar -czf" in content
        assert "aws s3 cp" in content

        # Verify backup paths
        assert "backup/" in content
        assert "database/" in content
        assert "files/" in content


def test_restore_script():
    # Test restore script
    scripts_dir = Path("scripts")

    # Test restore script
    restore_script = scripts_dir / "restore.sh"
    assert restore_script.exists()
    assert os.access(restore_script, os.X_OK)

    with open(restore_script, "r") as f:
        content = f.read()

        # Verify restore commands
        assert "pg_restore" in content
        assert "tar -xzf" in content
        assert "aws s3 cp" in content

        # Verify restore paths
        assert "backup/" in content
        assert "database/" in content
        assert "files/" in content


def test_monitoring_script():
    # Test monitoring script
    scripts_dir = Path("scripts")

    # Test monitoring script
    monitor_script = scripts_dir / "monitor.sh"
    assert monitor_script.exists()
    assert os.access(monitor_script, os.X_OK)

    with open(monitor_script, "r") as f:
        content = f.read()

        # Verify monitoring commands
        assert "kubectl get" in content
        assert "kubectl describe" in content
        assert "kubectl logs" in content

        # Verify monitoring paths
        assert "logs/" in content
        assert "metrics/" in content


def test_security_script():
    # Test security script
    scripts_dir = Path("scripts")

    # Test security script
    security_script = scripts_dir / "security.sh"
    assert security_script.exists()
    assert os.access(security_script, os.X_OK)

    with open(security_script, "r") as f:
        content = f.read()

        # Verify security commands
        assert "openssl" in content
        assert "chmod" in content
        assert "chown" in content

        # Verify security paths
        assert "certs/" in content
        assert "keys/" in content


def test_cleanup_script():
    # Test cleanup script
    scripts_dir = Path("scripts")

    # Test cleanup script
    cleanup_script = scripts_dir / "cleanup.sh"
    assert cleanup_script.exists()
    assert os.access(cleanup_script, os.X_OK)

    with open(cleanup_script, "r") as f:
        content = f.read()

        # Verify cleanup commands
        assert "rm -rf" in content
        assert "find" in content
        assert "kubectl delete" in content

        # Verify cleanup paths
        assert "tmp/" in content
        assert "logs/" in content
        assert "cache/" in content


def test_environment_setup_script():
    # Test environment setup script
    setup_script = Path("scripts/setup_env.sh")
    assert setup_script.exists()
    assert os.access(setup_script, os.X_OK)

    # Verify script contents
    with open(setup_script, "r") as f:
        content = f.read()

        # Verify required commands
        assert "python -m venv .venv" in content
        assert "pip install -r requirements.txt" in content
        assert "cp .env.example .env" in content


def test_database_migration_script():
    # Test database migration script
    migrate_script = Path("scripts/migrate_db.sh")
    assert migrate_script.exists()
    assert os.access(migrate_script, os.X_OK)

    # Verify script contents
    with open(migrate_script, "r") as f:
        content = f.read()

        # Verify required commands
        assert "alembic upgrade head" in content
        assert "python scripts/create_admin.py" in content


def test_monitoring_setup_script():
    # Test monitoring setup script
    monitor_script = Path("scripts/setup_monitoring.sh")
    assert monitor_script.exists()
    assert os.access(monitor_script, os.X_OK)

    # Verify script contents
    with open(monitor_script, "r") as f:
        content = f.read()

        # Verify required commands
        assert "pip install prometheus-client" in content
        assert "python scripts/start_monitoring.py" in content


def test_security_setup_script():
    # Test security setup script
    security_script = Path("scripts/setup_security.sh")
    assert security_script.exists()
    assert os.access(security_script, os.X_OK)

    # Verify script contents
    with open(security_script, "r") as f:
        content = f.read()

        # Verify required commands
        assert "openssl req -x509" in content
        assert "chmod 600" in content


def test_backup_script():
    # Test backup script
    backup_script = Path("scripts/backup.sh")
    assert backup_script.exists()
    assert os.access(backup_script, os.X_OK)

    # Verify script contents
    with open(backup_script, "r") as f:
        content = f.read()

        # Verify required commands
        assert "pg_dump" in content
        assert "tar -czf" in content


def test_restore_script():
    # Test restore script
    restore_script = Path("scripts/restore.sh")
    assert restore_script.exists()
    assert os.access(restore_script, os.X_OK)

    # Verify script contents
    with open(restore_script, "r") as f:
        content = f.read()

        # Verify required commands
        assert "pg_restore" in content
        assert "tar -xzf" in content


def test_health_check_script():
    # Test health check script
    health_script = Path("scripts/check_health.sh")
    assert health_script.exists()
    assert os.access(health_script, os.X_OK)

    # Verify script contents
    with open(health_script, "r") as f:
        content = f.read()

        # Verify required commands
        assert "curl" in content
        assert "jq" in content


def test_log_rotation_script():
    # Test log rotation script
    log_script = Path("scripts/rotate_logs.sh")
    assert log_script.exists()
    assert os.access(log_script, os.X_OK)

    # Verify script contents
    with open(log_script, "r") as f:
        content = f.read()

        # Verify required commands
        assert "logrotate" in content
        assert "compress" in content


def test_script_permissions():
    # Test script permissions
    scripts_dir = Path("scripts")
    assert scripts_dir.exists()

    for script in scripts_dir.glob("*.sh"):
        assert os.access(script, os.X_OK), f"Script {script} is not executable"

        # Verify script has proper shebang
        with open(script, "r") as f:
            first_line = f.readline().strip()
            assert first_line.startswith("#!/bin/"), f"Script {script} missing shebang"

        # Verify script has proper line endings
        with open(script, "rb") as f:
            content = f.read()
            assert b"\r\n" not in content, f"Script {script} has Windows line endings"
