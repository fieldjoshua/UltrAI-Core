# UltraAI Automated Pricing Updater

This tool automatically fetches the latest pricing data from major LLM providers and updates your UltraAI backend components with current pricing information.

## Features

- **Automated Scraping**: Fetches pricing data from OpenAI, Anthropic, Google, Cohere, AI21 and AWS
- **Smart Updating**: Only updates when prices change significantly (by default, 10% or more)
- **Model Mapping**: Maps external provider/model names to UltraAI's internal IDs
- **Historical Tracking**: Keeps records of all pricing changes over time
- **Email Alerts**: Sends notifications when significant price changes are detected
- **Dry Run Mode**: Allows checking for changes without modifying files
- **Safe Fallbacks**: Falls back to existing prices when scraping fails, maintaining stability
- **Anomaly Detection**: Flags suspicious price changes that may require manual validation

## Setup

### Easy Setup (Recommended)

The easiest way to set up is using the provided setup script:

```bash
# Make the script executable
chmod +x backend/setup_pricing_updater.sh

# Run the setup script
./backend/setup_pricing_updater.sh
```

This script will:
- Check if you're in a virtual environment (recommended)
- Create necessary directories 
- Install all dependencies
- Test imports to ensure everything is working
- Handle common dependency issues automatically

### Manual Setup

If you prefer to set up manually:

1. Install dependencies using the provided requirements file:
   ```bash
   pip install -r backend/pricing_updater_requirements.txt
   ```

2. Set environment variables for alert emails (optional):
   ```bash
   export ULTRAI_ALERT_EMAIL="your-email@example.com"
   export ULTRAI_SMTP_SERVER="smtp.gmail.com"
   export ULTRAI_SMTP_PORT="587"
   export ULTRAI_SMTP_USER="your-smtp-username"
   export ULTRAI_SMTP_PASSWORD="your-smtp-password"
   ```

## Usage

### Manual Run

```bash
# Run with default settings (will update files if changes detected)
python backend/pricing_updater.py

# Run without making changes (dry run)
python backend/pricing_updater.py --dry-run

# Force update even if no changes detected
python backend/pricing_updater.py --force

# Specify email for alerts
python backend/pricing_updater.py --alert-email="your-email@example.com"
```

### Automated Scheduling

#### Using cron (Linux/macOS)

Set up a weekly check by adding to your crontab:

```bash
# Run every Sunday at midnight
0 0 * * 0 cd /path/to/UltraAI && python backend/pricing_updater.py
```

#### Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create a new task to run weekly
3. Action: Start a program
4. Program: `python`
5. Arguments: `backend/pricing_updater.py`
6. Start in: `C:\path\to\UltraAI`

## How It Works

### Scraping & Fallback Mechanism

The pricing updater follows a safe approach to ensure pricing stability:

1. First, it attempts to scrape current pricing from provider websites
2. If scraping succeeds, it compares the new prices with existing ones
3. If scraping fails for any provider, it uses your existing prices as fallbacks
4. Only when there's no existing pricing data does it resort to hardcoded values
5. Changes are only applied if a significant difference is detected (10% by default)

This prioritizes stability and ensures that temporary scraping issues don't disrupt your pricing data.

### Anomaly Detection

The system incorporates industry-standard anomaly detection with configurable thresholds:

- **Critical Anomalies**: Changes of 100% or more (doubling or halving of price)
- **High Price Increases**: Increases of 50% or more
- **Suspiciously Low Prices**: Decreases of 60% or more
- **Context Window Anomalies**: Changes of 200% or more in context window size

These thresholds are based on industry patterns and help identify potential errors or unexpected changes in provider pricing. All anomalies are:

1. Logged with appropriate severity level
2. Included in email alerts with warning indicators
3. Presented for manual validation before proceeding

You can adjust these thresholds in the `pricing_updater.py` file according to your specific needs.

## Customization

### Adjusting Price Change Threshold

By default, the script alerts on price changes of 10% or more. You can adjust this by modifying the `PRICE_CHANGE_THRESHOLD` variable in `pricing_updater.py`.

### Adjusting Anomaly Detection Thresholds

The anomaly detection thresholds can be customized by modifying these variables:

```python
# At the top of pricing_updater.py
PRICE_ANOMALY_LOW_THRESHOLD = 0.6   # 60% price drop triggers anomaly warning
PRICE_ANOMALY_HIGH_THRESHOLD = 0.5  # 50% price increase triggers anomaly warning
PRICE_ANOMALY_CRITICAL_THRESHOLD = 1.0  # 100% price change triggers critical warning
```

### Adding New Models

When a new model is released, you'll need to:

1. Update the `_get_internal_id` method to map the provider and model name to your internal ID
2. For the first run, you might need to manually add the model to your `ultra_models.py` file

### Customizing Web Scraping

The script includes basic scraping logic for major providers, but website structures can change. If you encounter scraping issues:

1. Check the provider's pricing page HTML structure
2. Update the relevant `_fetch_<provider>_pricing` method
3. If scraping is unreliable, you can rely on the fallback to existing prices

## Directories and Files

- `pricing_history/`: Contains historical pricing data and change logs
- `current_pricing.json`: Latest pricing data in JSON format
- `pricing_updater.log`: Log file with detailed operation information
- `pricing_updater_requirements.txt`: Dependencies required for the script
- `setup_pricing_updater.sh`: Setup script to install dependencies and fix common issues

## Troubleshooting

### Dependency Issues

If you encounter dependency errors:
- Run the setup script: `./backend/setup_pricing_updater.sh`
- Make sure you've installed all dependencies using the requirements file
- Use a virtual environment to avoid package conflicts
- For the specific "six.moves" error, ensure the six package is installed

#### Fixing "No module named 'six.moves'" Error

If you encounter the specific error `ModuleNotFoundError: No module named 'six.moves'`:

```
# Install the six package directly
pip install six

# Then reinstall pandas (which depends on six)
pip install pandas --upgrade

# Alternatively, reinstall all requirements
pip install -r backend/pricing_updater_requirements.txt --upgrade
```

This error occurs because pandas requires the 'six' package through its dateutil dependency.

### Scraping Issues

If the script fails to scrape pricing:
- Don't worry - the script will fall back to your existing prices
- Check that the target website hasn't changed its structure
- Verify your internet connection
- Look for any rate limiting or IP blocking

### Price Anomaly Warnings

If you receive anomaly warnings in the logs or email alerts:
1. **Don't panic** - these are cautionary flags, not errors
2. **Manually verify** the changes against the provider's official pricing page
3. **If legitimate**, the changes will be applied normally
4. **If incorrect**, you can:
   - Fix the scraper for that provider
   - Run in dry-run mode to test your fixes
   - Manually update the pricing in `ultra_models.py` if needed

### File Update Issues

If files aren't being updated:
- Ensure file paths are correct
- Check file permissions
- Look for unexpected content format in the target files

## Contributing

When adding support for new providers:
1. Create a new `_fetch_<provider>_pricing` method
2. Update the `_get_internal_id` method to map the new provider's models
3. Add fallback data for the provider 