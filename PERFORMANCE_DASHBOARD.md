# Performance Dashboard for Ultra Framework

## Overview

The Performance Dashboard provides real-time metrics and visualization for monitoring the Ultra Framework's performance. It offers a comprehensive view of system health, resource utilization, and application metrics to help developers and administrators optimize and troubleshoot the application.

## Features

### System Overview
- **CPU Usage**: Real-time and historical CPU utilization with trend indicators
- **Memory Usage**: Current and historical memory consumption with trend analysis
- **Disk Usage**: Storage space utilization percentage

### Performance Metrics
- **Requests Processed**: Number of API requests handled by the system
- **Documents Processed**: Total number of documents processed through the system
- **Total Chunks**: Number of text chunks created from document processing
- **Average Processing Time**: Mean time taken to process requests
- **Memory Cache Size**: Number of items stored in the memory cache
- **Peak Memory Usage**: Maximum memory utilization observed

### Efficiency Metrics
- **Average Document Processing Time**: Time taken on average to process a document
- **Chunks per Document**: Average number of chunks generated per document
- **Cache Hit Rate**: Percentage of requests served from cache vs. from processing

### System Information
- **Uptime**: Total time the server has been running
- **Server Started**: Timestamp when the server was initialized
- **System Status**: Current operational status
- **Platform**: Operating system information
- **CPU Cores**: Number of CPU cores available
- **Total Memory**: System memory capacity
- **Python Version**: Version of Python running the backend

## Usage

### Accessing the Dashboard
1. Start the Ultra Framework application
2. Navigate to `/dashboard` in your browser or click the dashboard icon in the main app
3. The dashboard will automatically load with the latest metrics

### Dashboard Controls
- **Refresh**: Manually update the metrics data
- **Auto-refresh**: Toggle automatic refresh (updates every 5 seconds when enabled)
- **Home**: Return to the main application

### Interpreting Metrics
- **Trend Indicators**: Upward (green) or downward (red) arrows show metric trends
- **Time Series Charts**: Small spark line charts show historical data for key metrics
- **Formatting**: All metrics are presented in appropriate units (MB, seconds, %)

## Technical Implementation

The Performance Dashboard connects to the following backend endpoints:
- `/api/metrics`: Provides current performance metrics
- `/api/metrics/history`: Returns historical metrics data for time-series visualization
- `/health`: Returns system health and resource utilization information

The dashboard uses React components with optimization techniques like:
- Memoization of components and calculations
- Efficient rendering of time-series data
- Controlled real-time updates to minimize resource usage

## Extending the Dashboard

To add new metrics to the dashboard:
1. Update the backend metrics collection in `backend/main.py`
2. Add new metrics to the relevant state interfaces in `PerformanceDashboard.tsx`
3. Add visualization components using the existing `MetricCard` pattern

## Troubleshooting

If the dashboard shows no data:
- Verify the backend server is running
- Check that the API endpoints are accessible
- Confirm the API URL configuration in the dashboard component
- Check browser console for any error messages

---

*Note: The Performance Dashboard is designed to have minimal impact on the system's performance while providing valuable insights.* 