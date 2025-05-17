#!/usr/bin/env python3
"""
Health check script for Ultra backend.

This script checks the health of the Ultra backend and reports the status
of various services and dependencies. It can be used as a command-line tool
or as part of a monitoring system.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

import requests

# Default API URL
DEFAULT_API_URL = "http://localhost:8000"

# ANSI color codes for terminal output
COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


def color_text(text, color):
    """Apply color to text for terminal output"""
    if sys.stdout.isatty():
        return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"
    return text


def color_status(status):
    """Apply appropriate color to a status value"""
    status_colors = {
        "ok": "green",
        "degraded": "yellow",
        "critical": "red",
        "unavailable": "red",
        "unknown": "magenta",
    }
    return color_text(status, status_colors.get(status.lower(), "reset"))


def format_time(seconds):
    """Format time in seconds to a human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.1f}m"
    elif seconds < 86400:
        return f"{seconds / 3600:.1f}h"
    else:
        return f"{seconds / 86400:.1f}d"


def make_request(url, params=None):
    """Make a request to the API and return JSON response"""
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print(color_text(f"Error: Could not connect to {url}", "red"))
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(color_text(f"Error: Connection to {url} timed out", "red"))
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(color_text(f"Error: HTTP error {e}", "red"))
        sys.exit(1)
    except json.JSONDecodeError:
        print(color_text(f"Error: Invalid JSON response from {url}", "red"))
        sys.exit(1)


def print_basic_health(data):
    """Print basic health information"""
    status = data.get("status", "unknown")
    uptime = data.get("uptime", 0)

    print(f"Status: {color_status(status)}")
    print(f"Uptime: {color_text(format_time(uptime), 'cyan')}")


def print_system_health(data):
    """Print system health information"""
    details = data.get("details", {})
    memory = details.get("memory", {})
    disk = details.get("disk", {})
    cpu = details.get("cpu", {})

    print("\n" + color_text("System Health:", "bold"))
    print(
        f"Memory: {memory.get('percent', 0)}% used "
        f"({memory.get('used_gb', 0):.1f}GB / {memory.get('total_gb', 0):.1f}GB)"
    )
    print(
        f"Disk: {disk.get('percent', 0)}% used "
        f"({disk.get('used_gb', 0):.1f}GB / {disk.get('total_gb', 0):.1f}GB)"
    )
    print(
        f"CPU: {cpu.get('percent', 0)}% used "
        f"({cpu.get('cores', 0)} cores / {cpu.get('logical_cores', 0)} logical cores)"
    )


def print_service_health(service, data):
    """Print information about a specific service"""
    status = data.get("status", "unknown")
    message = data.get("message", "")
    details = data.get("details", {})
    using_fallback = data.get("using_fallback", False)

    print(f"  {service}: {color_status(status)}")
    print(f"    {message}")

    if using_fallback:
        print(f"    {color_text('Using fallback implementation', 'yellow')}")

    # Print interesting details based on service type
    if service == "database":
        if "host" in details:
            print(f"    Host: {details.get('host')}:{details.get('port', '')}")
        if "database" in details:
            print(f"    Database: {details.get('database')}")
    elif service == "redis":
        if "type" in details:
            print(f"    Type: {details.get('type')}")
        if "items_count" in details:
            print(f"    Items in cache: {details.get('items_count')}")
    elif service in ["openai", "anthropic", "google"]:
        if "api_key_configured" in data:
            api_key = "Yes" if data.get("api_key_configured") else "No"
            print(f"    API Key: {api_key}")
        if "duration_ms" in data:
            print(f"    Response time: {data.get('duration_ms')}ms")


def print_all_services(services):
    """Print information about all services"""
    print("\n" + color_text("Services:", "bold"))

    # Group by service type
    service_types = {}
    for name, data in services.items():
        service_type = None

        # Try to infer service type
        if name in ["database", "postgres"]:
            service_type = "Database"
        elif name in ["redis", "cache"]:
            service_type = "Cache"
        elif name in ["openai", "anthropic", "google"]:
            service_type = "LLM Provider"
        elif name in ["system"]:
            service_type = "System"
        elif name in ["storage"]:
            service_type = "Storage"
        elif name in ["network"]:
            service_type = "Network"
        else:
            service_type = "Other"

        if service_type not in service_types:
            service_types[service_type] = {}
        service_types[service_type][name] = data

    # Print by service type
    for service_type, services in service_types.items():
        print(f"\n{color_text(service_type, 'bold')}:")
        for name, data in services.items():
            print_service_health(name, data)


def print_llm_providers(providers):
    """Print information about LLM providers"""
    print("\n" + color_text("LLM Providers:", "bold"))
    for name, data in providers.items():
        print_service_health(name, data)


def print_dependencies(dependencies):
    """Print information about dependencies"""
    print("\n" + color_text("Dependencies:", "bold"))

    # Group by availability
    available = []
    unavailable = []

    for name, data in dependencies.items():
        if data.get("is_available"):
            available.append((name, data))
        else:
            unavailable.append((name, data))

    # Print available dependencies
    if available:
        print(color_text("  Available:", "green"))
        for name, data in available:
            required = "*" if data.get("is_required") else ""
            print(f"    {name}{required}: {data.get('name', '')}")

    # Print unavailable dependencies
    if unavailable:
        print(color_text("  Unavailable:", "yellow"))
        for name, data in unavailable:
            required = "*" if data.get("is_required") else ""
            print(f"    {name}{required}: {data.get('name', '')}")
            if data.get("error"):
                print(f"      Error: {data.get('error')}")
            if data.get("installation_cmd"):
                print(f"      Install: {data.get('installation_cmd')}")

    print("\n  * Required dependencies")


def print_feature_flags(features):
    """Print information about feature flags"""
    print("\n" + color_text("Feature Flags:", "bold"))

    # Group by enabled/disabled
    enabled = []
    disabled = []

    for name, enabled_flag in features.items():
        if enabled_flag:
            enabled.append(name)
        else:
            disabled.append(name)

    # Print enabled features
    if enabled:
        print(color_text("  Enabled:", "green"))
        for name in enabled:
            print(f"    {name}")

    # Print disabled features
    if disabled:
        print(color_text("  Disabled:", "yellow"))
        for name in disabled:
            print(f"    {name}")


def check_basic_health(api_url):
    """Check and print basic health information"""
    url = f"{api_url}/health"
    data = make_request(url)

    print(color_text("\nBasic Health Check:", "bold"))
    print_basic_health(data)

    return data.get("status") == "ok"


def check_detailed_health(api_url):
    """Check and print detailed health information"""
    url = f"{api_url}/api/health"
    params = {"detail": "true", "include_system": "true"}
    data = make_request(url, params)

    print(color_text("\nDetailed Health Check:", "bold"))
    print_basic_health(data)

    # Print failing services if any
    if "failing_services" in data:
        failing = data.get("failing_services", [])
        print(color_text(f"\nFailing services: {', '.join(failing)}", "red"))

    # Print system metrics if available
    if "system" in data:
        system = data.get("system", {})
        memory = system.get("memory", {})
        disk = system.get("disk", {})

        print("\n" + color_text("System Resources:", "bold"))
        print(
            f"  Memory: {memory.get('percent_used', 0)}% used "
            f"({memory.get('available_gb', 0):.1f}GB available)"
        )
        print(
            f"  Disk: {disk.get('percent_used', 0)}% used "
            f"({disk.get('free_gb', 0):.1f}GB free)"
        )

    # Print services
    if "services" in data:
        print_all_services(data.get("services", {}))

    # Print dependencies
    if "dependencies" in data:
        print_dependencies(data.get("dependencies", {}))

    # Print feature flags
    if "features" in data:
        print_feature_flags(data.get("features", {}))

    return data.get("status") == "ok"


def check_system_health(api_url):
    """Check and print system health information"""
    url = f"{api_url}/api/health/system"
    data = make_request(url)

    print(color_text("\nSystem Health Check:", "bold"))
    status = data.get("status", "unknown")
    message = data.get("message", "")

    print(f"Status: {color_status(status)}")
    print(f"Message: {message}")

    print_system_health(data)

    return status == "ok"


def check_llm_health(api_url):
    """Check and print LLM provider health information"""
    url = f"{api_url}/api/health/llm"
    data = make_request(url)

    print(color_text("\nLLM Provider Health Check:", "bold"))
    status = data.get("status", "unknown")

    print(f"Overall status: {color_status(status)}")

    if "providers" in data:
        print_llm_providers(data.get("providers", {}))

    return status == "ok"


def main():
    """Main function to run the script"""
    parser = argparse.ArgumentParser(description="Check health of Ultra backend.")
    parser.add_argument("--url", default=DEFAULT_API_URL, help="API URL")
    parser.add_argument(
        "--basic", action="store_true", help="Run basic health check only"
    )
    parser.add_argument(
        "--system", action="store_true", help="Run system health check only"
    )
    parser.add_argument(
        "--llm", action="store_true", help="Run LLM provider health check only"
    )
    parser.add_argument("--all", action="store_true", help="Run all health checks")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument(
        "--monitor", action="store_true", help="Run in monitor mode (continuous)"
    )
    parser.add_argument(
        "--interval", type=int, default=60, help="Monitoring interval in seconds"
    )

    args = parser.parse_args()

    if args.json:
        # Output in JSON format
        if args.all or (not args.basic and not args.system and not args.llm):
            url = f"{args.url}/api/health"
            params = {"detail": "true", "include_system": "true"}
            data = make_request(url, params)
            print(json.dumps(data, indent=2))
        elif args.basic:
            url = f"{args.url}/health"
            data = make_request(url)
            print(json.dumps(data, indent=2))
        elif args.system:
            url = f"{args.url}/api/health/system"
            data = make_request(url)
            print(json.dumps(data, indent=2))
        elif args.llm:
            url = f"{args.url}/api/health/llm"
            data = make_request(url)
            print(json.dumps(data, indent=2))
    elif args.monitor:
        # Run in monitor mode
        try:
            print(
                color_text(
                    f"Monitoring Ultra health (Ctrl+C to stop, interval: {args.interval}s)",
                    "bold",
                )
            )
            while True:
                clear_screen()
                print(
                    color_text(
                        f"Ultra Health Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        "bold",
                    )
                )

                if args.all or (not args.basic and not args.system and not args.llm):
                    check_detailed_health(args.url)
                elif args.basic:
                    check_basic_health(args.url)
                elif args.system:
                    check_system_health(args.url)
                elif args.llm:
                    check_llm_health(args.url)

                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
    else:
        # Run health checks
        if args.all or (not args.basic and not args.system and not args.llm):
            check_detailed_health(args.url)

        if args.basic:
            check_basic_health(args.url)

        if args.system:
            check_system_health(args.url)

        if args.llm:
            check_llm_health(args.url)


def clear_screen():
    """Clear the terminal screen"""
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


if __name__ == "__main__":
    main()
