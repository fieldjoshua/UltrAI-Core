# Port Management

This document describes the port management utilities and practices for the Ultra project.

## Overview

Port conflicts are a common issue during development, especially when multiple services need to run on specific ports. The port management utilities in this project provide automated solutions for detecting and resolving port conflicts.

## Port Clearing Utility

The `clear_port.sh` script provides a utility for detecting and clearing processes running on specific ports. It can be used both as a standalone script and as a function sourced by other scripts.

### Usage as Standalone Script

```bash
# Clear a specific port
./scripts/clear_port.sh 8085
```

### Usage as Sourced Function

```bash
# Source the script
source ./scripts/clear_port.sh

# Clear a specific port
clear_port 8085
```

### Integration in Server Scripts

The port clearing utility is integrated into several server scripts:

- `scripts/start-dev.sh` - Clears the port before starting the development server
- `scripts/start-ultra-with-modelrunner.sh` - Clears the port before starting with model runner
- `scripts/test_production.sh` - Includes port clearing in the cleanup process

## API Port Management

The `kill_api_ports.sh` script specifically targets API server ports. It provides a convenient way to kill processes on API ports before starting API servers.

### Usage

```bash
# Kill processes on the default API port (8085)
./scripts/kill_api_ports.sh

# Kill processes on a specific port
./scripts/kill_api_ports.sh 8000
```

## Path Handling

The path handling in `config.py` has been improved to properly handle both relative and absolute paths, making it more compatible with Docker environments:

- Relative paths are automatically converted to absolute paths
- Directory creation failures are handled gracefully with fallbacks to in-memory alternatives
- Clear error messages and logging for path-related issues

## Common Development Workflow

1. **Before Starting a Server**:
   ```bash
   # Clear the required port
   ./scripts/clear_port.sh 8085
   
   # Start the server
   python -m uvicorn backend.app:app --port 8085
   ```

2. **Automated Workflow**:
   ```bash
   # Use start scripts with integrated port clearing
   ./scripts/start-dev.sh
   ```

3. **Multiple Servers**:
   ```bash
   # Clear ports for multiple services
   ./scripts/clear_port.sh 8085  # API server
   ./scripts/clear_port.sh 3000  # Frontend server
   ./scripts/clear_port.sh 6379  # Redis
   ```

## Troubleshooting

### Common Port Issues

1. **Permission Denied**:
   - Make sure you have the necessary permissions to kill processes
   - Try running the script with sudo if needed

2. **Port Still in Use After Clearing**:
   - Some processes may restart automatically
   - Check for supervisor or systemd services that may be restarting processes
   - Use `lsof -i :PORT` to manually inspect what's using the port

3. **Docker Conflicts**:
   - Docker containers may be binding to ports
   - Use `docker ps` to check for running containers
   - Stop or reconfigure containers that are using the required ports

## Best Practices

1. **Port Standardization**:
   - Use consistent ports for specific services across development environments
   - Document standard ports in `.env.example` and documentation

2. **Environment Variables**:
   - Use environment variables for port configuration
   - Allow overriding default ports through environment variables

3. **Graceful Startup**:
   - Always clear ports before starting services
   - Include proper error handling for port conflicts

4. **Testing**:
   - Include port clearing in test scripts for reliable test execution
   - Clear ports during cleanup after tests

## Future Enhancements

Potential enhancements to the port management system:

1. **Port Reservation System**:
   - Implement a system to reserve ports for specific services
   - Prevent port conflicts by coordinating port usage

2. **Dynamic Port Assignment**:
   - Fall back to alternative ports when a preferred port is unavailable
   - Communicate assigned ports to dependent services

3. **Health Check Integration**:
   - Incorporate port status into the health check system
   - Monitor port availability as part of system health