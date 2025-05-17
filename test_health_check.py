#!/usr/bin/env python3
"""
Simple test for the health check module.

This script tests the health check utilities without requiring the full application context.
"""

import os
import socket
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the health check module
from backend.utils.health_check import (
    HealthCheck,
    HealthStatus,
    ServiceType,
    check_network_health,
    check_system_health,
    health_check_registry,
)


class TestHealthCheck(unittest.TestCase):
    """Test health check utilities"""

    def test_health_check_registry(self):
        """Test the health check registry"""

        # Create a simple health check
        def mock_check():
            return {
                "status": HealthStatus.OK,
                "message": "Test OK",
                "timestamp": "2025-05-01T12:00:00Z",
            }

        # Register it
        health_check = HealthCheck(
            name="test",
            service_type=ServiceType.CUSTOM,
            check_fn=mock_check,
            description="Test health check",
            is_critical=False,
        )

        # Register with the registry
        health_check_registry.register(health_check)

        # Verify it's registered
        self.assertIn("test", health_check_registry.get_all())

        # Check that it works
        result = health_check_registry.get("test").check()
        self.assertEqual(result["status"], HealthStatus.OK)
        self.assertEqual(result["message"], "Test OK")

        # Unregister it
        health_check_registry.unregister("test")
        self.assertNotIn("test", health_check_registry.get_all())

    def test_system_health(self):
        """Test the system health check function"""
        # This should always return a valid result
        result = check_system_health()

        # Verify structure
        self.assertIn("status", result)
        self.assertIn("message", result)
        self.assertIn("details", result)
        self.assertIn("timestamp", result)

        # Verify details
        details = result["details"]
        self.assertIn("memory", details)
        self.assertIn("disk", details)
        self.assertIn("cpu", details)

        # Verify status is one of the valid values
        self.assertIn(
            result["status"],
            [
                HealthStatus.OK,
                HealthStatus.DEGRADED,
                HealthStatus.CRITICAL,
                HealthStatus.UNAVAILABLE,
                HealthStatus.UNKNOWN,
            ],
        )

    @patch("backend.utils.health_check.socket.getaddrinfo")
    def test_network_health_success(self, mock_getaddrinfo):
        """Test the network health check function with success"""
        # Mock socket functions
        mock_socket = MagicMock()
        mock_socket.connect = MagicMock()
        mock_socket.close = MagicMock()

        # Mock getaddrinfo to return a list of addresses
        mock_getaddrinfo.return_value = [
            (2, 1, 6, "", ("93.184.216.34", 443)),
        ]

        # Mock socket.socket to return our mock socket
        with patch(
            "backend.utils.health_check.socket.socket", return_value=mock_socket
        ):
            # For HTTPS endpoints, we also need to mock the SSL context
            with patch("backend.utils.health_check.ssl.create_default_context"):
                with patch("backend.utils.health_check.socket.create_connection"):
                    # Run the check
                    result = check_network_health("example.com", 443)

        # Verify result
        self.assertEqual(result["status"], HealthStatus.OK)
        self.assertIn("Connection to example.com:443 successful", result["message"])

    @patch("backend.utils.health_check.socket.getaddrinfo")
    def test_network_health_failure(self, mock_getaddrinfo):
        """Test the network health check function with failure"""
        # Mock getaddrinfo to raise an exception
        mock_getaddrinfo.side_effect = socket.gaierror("Name or service not known")

        # Run the check
        result = check_network_health("nonexistent.example", 443)

        # Verify result
        self.assertEqual(result["status"], HealthStatus.UNAVAILABLE)
        self.assertIn("Failed to resolve nonexistent.example", result["message"])


if __name__ == "__main__":
    unittest.main()
