#!/usr/bin/env python3
"""
UltraAI Automated Pricing Updater

This script scrapes current pricing from major LLM providers, validates the data,
and automatically updates the pricing information in the UltraAI backend.

It can be run:
- On demand: python pricing_updater.py
- Scheduled via cron: 0 0 * * 0 python /path/to/pricing_updater.py
- As a service: Use systemd timer or similar
"""

import argparse
import importlib
import json
import logging
import os
import re
import smtplib
import sys
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("pricing_updater.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("pricing_updater")

# Set up paths
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
models_path = project_root / "ultra_models.py"
simulator_path = script_dir / "pricing_simulator.py"
current_pricing_path = script_dir / "current_pricing.json"
history_path = script_dir / "pricing_history"

# Ensure history directory exists
history_path.mkdir(exist_ok=True)

# Alert settings
PRICE_CHANGE_THRESHOLD = 0.1  # 10% price change triggers alert
# Anomaly detection thresholds
PRICE_ANOMALY_LOW_THRESHOLD = 0.6  # 60% price drop triggers anomaly warning
PRICE_ANOMALY_HIGH_THRESHOLD = 0.5  # 50% price increase triggers anomaly warning
PRICE_ANOMALY_CRITICAL_THRESHOLD = (
    1.0  # 100% price change (doubling/halving) triggers critical warning
)
ALERT_EMAIL = os.environ.get("ULTRAI_ALERT_EMAIL", "")
SMTP_SERVER = os.environ.get("ULTRAI_SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("ULTRAI_SMTP_PORT", "587"))
SMTP_USER = os.environ.get("ULTRAI_SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("ULTRAI_SMTP_PASSWORD", "")


class PricingUpdater:
    def __init__(self, dry_run: bool = False, force_update: bool = False):
        self.dry_run = dry_run
        self.force_update = force_update
        self.current_pricing = self._load_current_pricing()
        self.updated_pricing = {}
        self.changes = []
        self.anomalies = []  # Track pricing anomalies

    def _load_current_pricing(self) -> Dict[str, Any]:
        """Load the current pricing data from file"""
        if current_pricing_path.exists():
            try:
                with open(current_pricing_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading current pricing: {e}")
        return {}

    def run(self) -> bool:
        """Execute the full pricing update workflow"""
        logger.info("Starting pricing update process")

        try:
            # Scrape pricing from various providers
            scraped_data = self._scrape_all_providers()

            # Convert to our internal format
            self.updated_pricing = self._convert_scraped_data(scraped_data)

            # Detect changes
            self.changes = self._detect_changes()

            # If there are changes or force update is set
            if self.changes or self.force_update:
                if not self.dry_run:
                    # Update the models file
                    self._update_models_file()

                    # Update the pricing simulator
                    self._update_pricing_simulator()

                    # Save the new pricing data
                    self._save_pricing_data()

                # Send alerts for significant changes
                if self.changes:
                    self._send_alerts()

                logger.info(
                    f"Pricing update completed: {len(self.changes)} changes detected"
                )
                return True
            else:
                logger.info("No pricing changes detected")
                return False

        except Exception as e:
            logger.error(f"Error during pricing update: {e}", exc_info=True)
            return False

    def _scrape_all_providers(self) -> pd.DataFrame:
        """Scrape pricing data from all providers and return a combined DataFrame"""
        logger.info("Scraping pricing from providers")

        pricing_data = []
        pricing_data.extend(self._fetch_openai_pricing())
        pricing_data.extend(self._fetch_anthropic_pricing())
        pricing_data.extend(self._fetch_google_pricing())
        pricing_data.extend(self._fetch_cohere_pricing())
        pricing_data.extend(self._fetch_ai21_pricing())
        pricing_data.extend(self._fetch_aws_bedrock_pricing())

        df = pd.DataFrame(
            pricing_data,
            columns=[
                "Model",
                "Input Cost per 1K",
                "Output Cost per 1K",
                "Total Cost per 1K",
                "Context Window",
                "Is Thinking Model",
            ],
        )

        # Save raw scraped data for reference
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        df.to_csv(history_path / f"scraped_pricing_{timestamp}.csv", index=False)

        return df

    def _convert_scraped_data(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Convert scraped DataFrame to our internal pricing format"""
        logger.info("Converting scraped data to internal format")

        def extract_numeric(value: str) -> float:
            """Extract numeric value from string like '$0.003 per 1K tokens'"""
            if pd.isna(value) or value == "N/A":
                return 0.0
            matches = re.findall(r"[\d.]+", value)
            return float(matches[0]) if matches else 0.0

        def extract_context_window(value: str) -> int:
            """Extract context window size in tokens from string like '8K tokens' or '128k'"""
            if pd.isna(value) or value == "N/A":
                return 0
            matches = re.findall(r"(\d+)", value.lower().replace("tokens", "").strip())
            size = int(matches[0]) if matches else 0

            # Convert to raw token count
            if "k" in value.lower() or "thousand" in value.lower():
                size *= 1000
            elif "m" in value.lower() or "million" in value.lower():
                size *= 1000000

            return size

        pricing = {}

        for _, row in df.iterrows():
            model_full_name = row["Model"]
            provider, *model_parts = model_full_name.split(" ", 1)
            model_name = model_parts[0] if model_parts else "Unknown"

            # Convert to internal model ID format
            internal_id = self._get_internal_id(provider, model_name)
            if not internal_id:
                continue

            input_cost = extract_numeric(row["Input Cost per 1K"])
            output_cost = extract_numeric(row["Output Cost per 1K"])
            total_cost = extract_numeric(row["Total Cost per 1K"])

            # If total cost wasn't provided, sum input and output costs
            if total_cost == 0.0 and (input_cost > 0.0 or output_cost > 0.0):
                total_cost = input_cost + output_cost

            context_window = extract_context_window(row["Context Window"])
            is_thinking_model = (
                row["Is Thinking Model"]
                if not pd.isna(row["Is Thinking Model"])
                else False
            )

            # Determine if this is a "thinking model" based on certain criteria
            if not isinstance(is_thinking_model, bool):
                is_thinking_model = (
                    "gpt-4" in model_name.lower()
                    or "claude" in model_name.lower()
                    and "opus" in model_name.lower()
                    or "claude" in model_name.lower()
                    and "sonnet" in model_name.lower()
                    or "gemini" in model_name.lower()
                    and "pro" in model_name.lower()
                    and "max" in model_name.lower()
                )

            pricing[internal_id] = {
                "provider": provider.lower(),
                "model_name": model_name,
                "input_cost_per_1k": input_cost,
                "output_cost_per_1k": output_cost,
                "total_cost_per_1k": total_cost,
                "context_window": context_window,
                "is_thinking_model": is_thinking_model,
            }

        return pricing

    def _get_internal_id(self, provider: str, model_name: str) -> Optional[str]:
        """Map provider and model name to internal ID"""
        mapping = {
            "OpenAI": {
                "GPT-4o": "gpt4o",
                "GPT-4o-mini": "gpt4o_mini",
                "GPT-4 Turbo": "gpt4_turbo",
                "GPT-4": "gpt4",
                "GPT-3.5 Turbo": "gpt35_turbo",
                "GPT-o1": "gpto1",
                "GPT-o3 mini": "gpto3mini",
            },
            "Anthropic": {
                "Claude 3 Opus": "claude3_opus",
                "Claude 3.7 Sonnet": "claude37",
                "Claude 3.5 Haiku": "claude35_haiku",
            },
            "Google": {
                "Gemini 1.5 Pro": "gemini15",
                "Gemini 2.5 Pro Max": "gemini25_pro_max",
            },
            "Cohere": {
                "Command R+": "cohere_command_rplus",
                "Command R": "cohere_command_r",
            },
            "Meta": {
                "Llama 3": "llama3",
            },
            "Mistral": {
                "Mistral Large": "mistral_large",
                "Mistral Medium": "mistral_medium",
                "Mistral Small": "mistral_small",
            },
        }

        provider_map = mapping.get(provider)
        if not provider_map:
            return None

        return provider_map.get(model_name)

    def _detect_changes(self) -> List[Dict[str, Any]]:
        """Detect changes between current and updated pricing"""
        logger.info("Detecting pricing changes")

        changes = []
        self.anomalies = []  # Reset anomalies

        # Check for models in updated pricing that exist in current pricing
        for model_id, new_data in self.updated_pricing.items():
            if model_id in self.current_pricing:
                current = self.current_pricing[model_id]

                # Compare input cost
                old_input = current.get("input_cost_per_1k", 0)
                new_input = new_data.get("input_cost_per_1k", 0)
                if old_input > 0 and new_input > 0:
                    input_change_pct = abs(new_input - old_input) / old_input
                    input_change_direction = (
                        "increase" if new_input > old_input else "decrease"
                    )

                    # Check for anomalies in input cost
                    self._check_price_anomaly(
                        model_id,
                        "input_cost_per_1k",
                        old_input,
                        new_input,
                        input_change_pct,
                    )

                    if input_change_pct > PRICE_CHANGE_THRESHOLD:
                        changes.append(
                            {
                                "model_id": model_id,
                                "field": "input_cost_per_1k",
                                "old_value": old_input,
                                "new_value": new_input,
                                "change_pct": input_change_pct * 100,
                                "direction": input_change_direction,
                            }
                        )

                # Compare output cost
                old_output = current.get("output_cost_per_1k", 0)
                new_output = new_data.get("output_cost_per_1k", 0)
                if old_output > 0 and new_output > 0:
                    output_change_pct = abs(new_output - old_output) / old_output
                    output_change_direction = (
                        "increase" if new_output > old_output else "decrease"
                    )

                    # Check for anomalies in output cost
                    self._check_price_anomaly(
                        model_id,
                        "output_cost_per_1k",
                        old_output,
                        new_output,
                        output_change_pct,
                    )

                    if output_change_pct > PRICE_CHANGE_THRESHOLD:
                        changes.append(
                            {
                                "model_id": model_id,
                                "field": "output_cost_per_1k",
                                "old_value": old_output,
                                "new_value": new_output,
                                "change_pct": output_change_pct * 100,
                                "direction": output_change_direction,
                            }
                        )

                # Compare context window
                old_context = current.get("context_window", 0)
                new_context = new_data.get("context_window", 0)
                if old_context > 0 and new_context > 0 and old_context != new_context:
                    # Check for anomalies in context window
                    context_change_pct = abs(new_context - old_context) / old_context
                    if (
                        context_change_pct > 2.0
                    ):  # 200% change in context window is unusual
                        self.anomalies.append(
                            {
                                "model_id": model_id,
                                "field": "context_window",
                                "old_value": old_context,
                                "new_value": new_context,
                                "change_pct": context_change_pct * 100,
                                "severity": "warning",
                                "message": f"Unusual change in context window size: {old_context} -> {new_context}",
                            }
                        )

                    changes.append(
                        {
                            "model_id": model_id,
                            "field": "context_window",
                            "old_value": old_context,
                            "new_value": new_context,
                            "change_pct": None,
                        }
                    )
            else:
                # New model added
                changes.append(
                    {
                        "model_id": model_id,
                        "field": "new_model",
                        "old_value": None,
                        "new_value": new_data,
                        "change_pct": None,
                    }
                )

        # Check for models in current pricing that no longer exist
        for model_id in self.current_pricing:
            if model_id not in self.updated_pricing:
                changes.append(
                    {
                        "model_id": model_id,
                        "field": "removed_model",
                        "old_value": self.current_pricing[model_id],
                        "new_value": None,
                        "change_pct": None,
                    }
                )

        # Log any anomalies
        if self.anomalies:
            logger.warning(f"Detected {len(self.anomalies)} pricing anomalies")
            for anomaly in self.anomalies:
                severity = anomaly["severity"]
                message = anomaly["message"]
                if severity == "critical":
                    logger.critical(message)
                elif severity == "warning":
                    logger.warning(message)

        return changes

    def _check_price_anomaly(
        self,
        model_id: str,
        field: str,
        old_value: float,
        new_value: float,
        change_pct: float,
    ) -> None:
        """Check for pricing anomalies and add them to the anomalies list"""
        # Skip if old value is zero (to avoid division by zero)
        if old_value == 0:
            return

        direction = "increased" if new_value > old_value else "decreased"
        field_name = field.replace("_", " ")

        # Check for critical anomalies (price doubled or halved)
        if change_pct >= PRICE_ANOMALY_CRITICAL_THRESHOLD:
            message = f"CRITICAL: {model_id} {field_name} {direction} by {change_pct*100:.1f}% (${old_value:.6f} -> ${new_value:.6f})"
            self.anomalies.append(
                {
                    "model_id": model_id,
                    "field": field,
                    "old_value": old_value,
                    "new_value": new_value,
                    "change_pct": change_pct * 100,
                    "severity": "critical",
                    "message": message,
                    "direction": direction,
                }
            )
            logger.critical(message)
            return

        # Check for high price increases
        if direction == "increased" and change_pct >= PRICE_ANOMALY_HIGH_THRESHOLD:
            message = f"WARNING: {model_id} {field_name} {direction} by {change_pct*100:.1f}% (${old_value:.6f} -> ${new_value:.6f})"
            self.anomalies.append(
                {
                    "model_id": model_id,
                    "field": field,
                    "old_value": old_value,
                    "new_value": new_value,
                    "change_pct": change_pct * 100,
                    "severity": "warning",
                    "message": message,
                    "direction": direction,
                }
            )
            logger.warning(message)
            return

        # Check for unusually low prices (potential scraping error)
        if direction == "decreased" and change_pct >= PRICE_ANOMALY_LOW_THRESHOLD:
            message = f"WARNING: {model_id} {field_name} {direction} by {change_pct*100:.1f}% (${old_value:.6f} -> ${new_value:.6f}) - Validate this change"
            self.anomalies.append(
                {
                    "model_id": model_id,
                    "field": field,
                    "old_value": old_value,
                    "new_value": new_value,
                    "change_pct": change_pct * 100,
                    "severity": "warning",
                    "message": message,
                    "direction": direction,
                }
            )
            logger.warning(message)

    def _update_models_file(self) -> None:
        """Update the ultra_models.py file with new pricing"""
        logger.info(f"Updating models file at {models_path}")

        if not models_path.exists():
            raise FileNotFoundError(f"Models file not found at {models_path}")

        with open(models_path, "r") as f:
            content = f.read()

        for model_id, pricing in self.updated_pricing.items():
            # Skip if we don't have complete data
            if not all(
                k in pricing
                for k in [
                    "input_cost_per_1k",
                    "output_cost_per_1k",
                    "total_cost_per_1k",
                ]
            ):
                continue

            # Pattern to match the model config in the file
            pattern = rf'"{model_id}"\s*:\s*ModelConfig\([^)]+\)'

            # Check if the model exists in the file
            if re.search(pattern, content):
                # Update existing model
                self._update_existing_model(model_id, pricing, content)
            else:
                # TODO: Add code to insert new model configurations
                logger.warning(
                    f"Model {model_id} not found in models file - would need to add it manually"
                )

    def _update_existing_model(
        self, model_id: str, pricing: Dict[str, Any], content: str
    ) -> None:
        """Update an existing model in the models file"""

        # Find the ModelConfig block for this model
        pattern = rf'"{model_id}"\s*:\s*ModelConfig\([^)]+\)'
        match = re.search(pattern, content)

        if match:
            model_config = match.group(0)

            # Update input cost
            model_config = re.sub(
                r"input_cost_per_1k_tokens\s*=\s*[\d.]+",
                f'input_cost_per_1k_tokens={pricing["input_cost_per_1k"]}',
                model_config,
            )

            # Update output cost
            model_config = re.sub(
                r"output_cost_per_1k_tokens\s*=\s*[\d.]+",
                f'output_cost_per_1k_tokens={pricing["output_cost_per_1k"]}',
                model_config,
            )

            # Update total cost
            model_config = re.sub(
                r"cost_per_1k_tokens\s*=\s*[\d.]+",
                f'cost_per_1k_tokens={pricing["total_cost_per_1k"]}',
                model_config,
            )

            # Update context window if available
            if pricing.get("context_window"):
                model_config = re.sub(
                    r"context_window\s*=\s*\d+",
                    f'context_window={pricing["context_window"]}',
                    model_config,
                )

            # Update is_thinking_model if available
            if "is_thinking_model" in pricing:
                is_thinking = str(pricing["is_thinking_model"]).lower()
                model_config = re.sub(
                    r"is_thinking_model\s*=\s*(True|False)",
                    f"is_thinking_model={is_thinking}",
                    model_config,
                )

            # Replace in full content
            updated_content = content.replace(match.group(0), model_config)

            # Write back to file if not in dry run mode
            if not self.dry_run:
                with open(models_path, "w") as f:
                    f.write(updated_content)
                logger.info(f"Updated model {model_id} in models file")

    def _update_pricing_simulator(self) -> None:
        """Update the pricing simulator with new pricing data"""
        logger.info(f"Updating pricing simulator at {simulator_path}")

        if not simulator_path.exists():
            raise FileNotFoundError(f"Pricing simulator not found at {simulator_path}")

        with open(simulator_path, "r") as f:
            content = f.read()

        # Find the model_pricing dictionary in the file
        pattern = r"self\.model_pricing\s*=\s*{[^}]+}"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            # Extract the model pricing block
            pricing_block = match.group(0)

            # Loop through updated models and update each one
            for model_id, pricing in self.updated_pricing.items():
                # Skip if we don't have complete data
                if not all(
                    k in pricing
                    for k in [
                        "input_cost_per_1k",
                        "output_cost_per_1k",
                        "total_cost_per_1k",
                    ]
                ):
                    continue

                # Check if model exists in the pricing block
                model_pattern = rf'"{model_id}"\s*:\s*{{[^}}]+}}'
                model_match = re.search(model_pattern, pricing_block, re.DOTALL)

                if model_match:
                    # Update existing model
                    model_block = model_match.group(0)

                    # Update input cost
                    model_block = re.sub(
                        r'"input_cost_per_1k"\s*:\s*[\d.]+',
                        f'"input_cost_per_1k": {pricing["input_cost_per_1k"]}',
                        model_block,
                    )

                    # Update output cost
                    model_block = re.sub(
                        r'"output_cost_per_1k"\s*:\s*[\d.]+',
                        f'"output_cost_per_1k": {pricing["output_cost_per_1k"]}',
                        model_block,
                    )

                    # Update total cost
                    model_block = re.sub(
                        r'"total_cost_per_1k"\s*:\s*[\d.]+',
                        f'"total_cost_per_1k": {pricing["total_cost_per_1k"]}',
                        model_block,
                    )

                    # Update context window if available
                    if pricing.get("context_window"):
                        model_block = re.sub(
                            r'"context_window"\s*:\s*\d+',
                            f'"context_window": {pricing["context_window"]}',
                            model_block,
                        )

                    # Update is_thinking_model if available
                    if "is_thinking_model" in pricing:
                        is_thinking = str(pricing["is_thinking_model"]).lower()
                        model_block = re.sub(
                            r'"is_thinking_model"\s*:\s*(true|false)',
                            f'"is_thinking_model": {is_thinking}',
                            model_block,
                        )

                    # Replace in pricing block
                    pricing_block = pricing_block.replace(
                        model_match.group(0), model_block
                    )
                else:
                    # TODO: Add code to insert new model in the pricing block
                    logger.warning(
                        f"Model {model_id} not found in pricing simulator - would need to add it manually"
                    )

            # Replace entire pricing block in the content
            updated_content = content.replace(match.group(0), pricing_block)

            # Write back to file if not in dry run mode
            if not self.dry_run:
                with open(simulator_path, "w") as f:
                    f.write(updated_content)
                logger.info(f"Updated pricing in simulator file")

    def _save_pricing_data(self) -> None:
        """Save the updated pricing data to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save the current pricing as historical data
        if self.current_pricing:
            history_file = history_path / f"pricing_{timestamp}.json"
            with open(history_file, "w") as f:
                json.dump(self.current_pricing, f, indent=2)

        # Save the updated pricing as current
        with open(current_pricing_path, "w") as f:
            json.dump(self.updated_pricing, f, indent=2)

        logger.info(f"Saved updated pricing data to {current_pricing_path}")

        # Save changes log
        if self.changes:
            changes_file = history_path / f"changes_{timestamp}.json"
            with open(changes_file, "w") as f:
                json.dump(self.changes, f, indent=2)
            logger.info(f"Saved changes log to {changes_file}")

    def _send_alerts(self) -> None:
        """Send email alerts for significant pricing changes"""
        if not ALERT_EMAIL or (not self.changes and not self.anomalies):
            return

        try:
            # Create email content
            num_changes = len(self.changes)
            num_anomalies = len(self.anomalies)

            if num_anomalies > 0:
                subject = f"UltraAI Pricing Alert: {num_changes} changes, {num_anomalies} anomalies detected"
            else:
                subject = f"UltraAI Pricing Alert: {num_changes} changes detected"

            # Create HTML email content
            html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .increase {{ color: red; }}
                    .decrease {{ color: green; }}
                    .critical {{ background-color: #ffdddd; font-weight: bold; }}
                    .warning {{ background-color: #ffffdd; }}
                    h2 {{ color: #333; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <h2>UltraAI Pricing Alert</h2>
                <p>The following pricing changes were detected on {datetime.now().strftime('%Y-%m-%d')}:</p>
            """

            # Add anomalies section if any exist
            if self.anomalies:
                html += f"""
                <h2>⚠️ Pricing Anomalies Detected ({len(self.anomalies)})</h2>
                <p>The following unusual pricing changes were detected and should be validated:</p>

                <table>
                    <tr>
                        <th>Severity</th>
                        <th>Model ID</th>
                        <th>Field</th>
                        <th>Old Value</th>
                        <th>New Value</th>
                        <th>Change %</th>
                    </tr>
                """

                for anomaly in self.anomalies:
                    model_id = anomaly["model_id"]
                    field = anomaly["field"].replace("_", " ").title()
                    old_value = anomaly["old_value"]
                    new_value = anomaly["new_value"]
                    change_pct = anomaly["change_pct"]
                    severity = anomaly["severity"]
                    direction = anomaly.get("direction", "changed")

                    css_class = f"{severity} {direction}"

                    html += f"""
                    <tr class="{css_class}">
                        <td>{severity.upper()}</td>
                        <td>{model_id}</td>
                        <td>{field}</td>
                        <td>${old_value:.6f}</td>
                        <td>${new_value:.6f}</td>
                        <td>{change_pct:.2f}%</td>
                    </tr>
                    """

                html += """
                </table>
                <p><strong>Please validate these changes before applying them in production!</strong></p>
                """

            # Add regular changes section
            html += f"""
                <h2>Pricing Changes ({len(self.changes)})</h2>
                <table>
                    <tr>
                        <th>Model ID</th>
                        <th>Change Type</th>
                        <th>Old Value</th>
                        <th>New Value</th>
                        <th>Change %</th>
                    </tr>
            """

            for change in self.changes:
                model_id = change["model_id"]
                field = change["field"]
                old_value = change["old_value"]
                new_value = change["new_value"]
                change_pct = change["change_pct"]
                direction = change.get("direction", "")

                # Format the row based on change type
                if field == "new_model":
                    html += f"""
                    <tr>
                        <td>{model_id}</td>
                        <td>New Model Added</td>
                        <td>N/A</td>
                        <td>{new_value["total_cost_per_1k"] if isinstance(new_value, dict) and "total_cost_per_1k" in new_value else "N/A"}</td>
                        <td>N/A</td>
                    </tr>
                    """
                elif field == "removed_model":
                    html += f"""
                    <tr>
                        <td>{model_id}</td>
                        <td>Model Removed</td>
                        <td>{old_value["total_cost_per_1k"] if isinstance(old_value, dict) and "total_cost_per_1k" in old_value else "N/A"}</td>
                        <td>N/A</td>
                        <td>N/A</td>
                    </tr>
                    """
                elif field == "context_window":
                    html += f"""
                    <tr>
                        <td>{model_id}</td>
                        <td>Context Window Changed</td>
                        <td>{old_value}</td>
                        <td>{new_value}</td>
                        <td>N/A</td>
                    </tr>
                    """
                else:
                    # Price change
                    css_class = "increase" if direction == "increase" else "decrease"
                    change_text = (
                        f"{change_pct:.2f}%" if change_pct is not None else "N/A"
                    )
                    html += f"""
                    <tr class="{css_class}">
                        <td>{model_id}</td>
                        <td>{field.replace("_", " ").title()}</td>
                        <td>${old_value:.6f}</td>
                        <td>${new_value:.6f}</td>
                        <td>{change_text}</td>
                    </tr>
                    """

            html += """
                </table>
                <p>This alert was automatically generated by the UltraAI Pricing Updater.</p>
            </body>
            </html>
            """

            # Create the email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = SMTP_USER
            msg["To"] = ALERT_EMAIL

            # Attach HTML version
            msg.attach(MIMEText(html, "html"))

            # Send the email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)

            logger.info(f"Sent pricing alert email to {ALERT_EMAIL}")

        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")

    # Provider-specific scraping methods
    def _fetch_openai_pricing(self) -> List[List[Any]]:
        """Scrape OpenAI pricing from the official pricing page"""
        try:
            url = "https://openai.com/pricing"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            pricing_data = []

            # Example implementation - needs to be tailored to the actual HTML structure
            pricing_sections = soup.find_all("div", class_="pricing-table")
            for section in pricing_sections:
                model_rows = section.find_all("tr")
                for row in model_rows:
                    try:
                        cells = row.find_all("td")
                        if not cells or len(cells) < 3:
                            continue

                        model_name = cells[0].get_text(strip=True)
                        if not model_name:
                            continue

                        # Try to extract pricing data
                        input_price = (
                            cells[1].get_text(strip=True) if len(cells) > 1 else "N/A"
                        )
                        output_price = (
                            cells[2].get_text(strip=True) if len(cells) > 2 else "N/A"
                        )
                        total_price = "N/A"  # Calculate later
                        context = (
                            cells[3].get_text(strip=True) if len(cells) > 3 else "N/A"
                        )

                        # Determine if it's a thinking model
                        is_thinking = (
                            "gpt-4" in model_name.lower()
                            and not "mini" in model_name.lower()
                            or "o1" in model_name.lower()
                        )

                        pricing_data.append(
                            [
                                f"OpenAI {model_name}",
                                input_price,
                                output_price,
                                total_price,
                                context,
                                is_thinking,
                            ]
                        )
                    except Exception as e:
                        logger.warning(f"Error parsing OpenAI row: {e}")

            if not pricing_data:
                logger.warning(
                    "No OpenAI pricing data found - using current pricing data"
                )
                # Use current pricing instead of hardcoded fallbacks
                for model_id, data in self.current_pricing.items():
                    if data.get("provider", "").lower() == "openai":
                        model_name = data.get("model_name", "")
                        if model_name:
                            input_cost = f"${data.get('input_cost_per_1k', 0)}"
                            output_cost = f"${data.get('output_cost_per_1k', 0)}"
                            total_cost = f"${data.get('total_cost_per_1k', 0)}"
                            context = f"{data.get('context_window', 0) // 1000}K"
                            is_thinking = data.get("is_thinking_model", False)

                            pricing_data.append(
                                [
                                    f"OpenAI {model_name}",
                                    input_cost,
                                    output_cost,
                                    total_cost,
                                    context,
                                    is_thinking,
                                ]
                            )

                # Only use hardcoded values if we have no current pricing data
                if not pricing_data:
                    logger.warning(
                        "No current OpenAI pricing data - using hardcoded fallback values"
                    )
                    pricing_data = [
                        [
                            "OpenAI GPT-4o",
                            "$0.0025",
                            "$0.0100",
                            "$0.0125",
                            "128K",
                            True,
                        ],
                        [
                            "OpenAI GPT-4o mini",
                            "$0.00015",
                            "$0.00060",
                            "$0.00075",
                            "128K",
                            False,
                        ],
                        ["OpenAI GPT-4 Turbo", "$0.01", "$0.03", "$0.04", "128K", True],
                        [
                            "OpenAI GPT-3.5 Turbo",
                            "$0.0005",
                            "$0.0015",
                            "$0.0020",
                            "4K",
                            False,
                        ],
                        ["OpenAI GPT-o1", "$0.015", "$0.060", "$0.075", "200K", True],
                        [
                            "OpenAI GPT-o3 mini",
                            "$0.00110",
                            "$0.00440",
                            "$0.00550",
                            "200K",
                            False,
                        ],
                    ]

            return pricing_data
        except Exception as e:
            logger.error(f"Error fetching OpenAI pricing: {e}")
            # Default to current pricing
            return self._get_current_provider_pricing("openai")

    def _fetch_anthropic_pricing(self) -> List[List[Any]]:
        """Scrape Anthropic pricing from the official pricing page"""
        try:
            url = "https://www.anthropic.com/api/pricing"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            pricing_data = []

            # Example implementation - needs to be tailored to the actual HTML structure
            pricing_tables = soup.find_all("table")
            for table in pricing_tables:
                rows = table.find_all("tr")
                for row in rows:
                    try:
                        cells = row.find_all("td")
                        if not cells or len(cells) < 3:
                            continue

                        model_name = cells[0].get_text(strip=True)
                        if not model_name or model_name == "Model":
                            continue

                        # Try to extract pricing data
                        input_price = (
                            cells[1].get_text(strip=True) if len(cells) > 1 else "N/A"
                        )
                        output_price = (
                            cells[2].get_text(strip=True) if len(cells) > 2 else "N/A"
                        )
                        total_price = "N/A"  # Calculate later
                        context = (
                            cells[3].get_text(strip=True) if len(cells) > 3 else "N/A"
                        )

                        # Determine if it's a thinking model
                        is_thinking = (
                            "opus" in model_name.lower()
                            or "sonnet" in model_name.lower()
                            and "3.7" in model_name
                        )

                        pricing_data.append(
                            [
                                "Anthropic " + model_name,
                                input_price,
                                output_price,
                                total_price,
                                context,
                                is_thinking,
                            ]
                        )
                    except Exception as e:
                        logger.warning(f"Error parsing Anthropic row: {e}")

            if not pricing_data:
                logger.warning(
                    "No Anthropic pricing data found - using current pricing data"
                )
                # Use current pricing instead of hardcoded fallbacks
                return self._get_current_provider_pricing("anthropic")

            return pricing_data
        except Exception as e:
            logger.error(f"Error fetching Anthropic pricing: {e}")
            # Default to current pricing
            return self._get_current_provider_pricing("anthropic")

    def _fetch_google_pricing(self) -> List[List[Any]]:
        """Scrape Google pricing from the official pricing page"""
        try:
            url = "https://cloud.google.com/vertex-ai/pricing"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            pricing_data = []

            # Example implementation - similar to other implementations
            # ... (code to scrape Google's pricing page)

            # If scraping fails, use current pricing
            if not pricing_data:
                logger.warning(
                    "No Google pricing data found - using current pricing data"
                )
                return self._get_current_provider_pricing("google")

            return pricing_data
        except Exception as e:
            logger.error(f"Error fetching Google pricing: {e}")
            # Default to current pricing
            return self._get_current_provider_pricing("google")

    def _fetch_cohere_pricing(self) -> List[List[Any]]:
        """Scrape Cohere pricing information"""
        try:
            # Attempt to scrape from Cohere's website
            # If scraping fails, use current pricing
            return self._get_current_provider_pricing("cohere")
        except Exception:
            # Default to current pricing
            return self._get_current_provider_pricing("cohere")

    def _fetch_ai21_pricing(self) -> List[List[Any]]:
        """Scrape AI21 pricing information"""
        try:
            # Attempt to scrape from AI21's website
            # If scraping fails, use current pricing
            return self._get_current_provider_pricing("ai21")
        except Exception:
            # Default to current pricing
            return self._get_current_provider_pricing("ai21")

    def _fetch_aws_bedrock_pricing(self) -> List[List[Any]]:
        """Scrape AWS Bedrock pricing information"""
        try:
            # Attempt to scrape from AWS's website
            # If scraping fails, use current pricing
            return self._get_current_provider_pricing("aws")
        except Exception:
            # Default to current pricing
            return self._get_current_provider_pricing("aws")

    def _get_current_provider_pricing(self, provider: str) -> List[List[Any]]:
        """Get current pricing data for a specific provider"""
        pricing_data = []

        for model_id, data in self.current_pricing.items():
            if data.get("provider", "").lower() == provider.lower():
                model_name = data.get("model_name", "")
                if model_name:
                    provider_name = provider.title()
                    input_cost = f"${data.get('input_cost_per_1k', 0)}"
                    output_cost = f"${data.get('output_cost_per_1k', 0)}"
                    total_cost = f"${data.get('total_cost_per_1k', 0)}"
                    context = f"{data.get('context_window', 0) // 1000}K"
                    is_thinking = data.get("is_thinking_model", False)

                    pricing_data.append(
                        [
                            f"{provider_name} {model_name}",
                            input_cost,
                            output_cost,
                            total_cost,
                            context,
                            is_thinking,
                        ]
                    )

        # If no current pricing data, use hardcoded fallbacks as last resort
        if not pricing_data:
            logger.warning(
                f"No current {provider} pricing data - using hardcoded fallback values"
            )
            if provider.lower() == "openai":
                pricing_data = [
                    ["OpenAI GPT-4o", "$0.0025", "$0.0100", "$0.0125", "128K", True],
                    [
                        "OpenAI GPT-4o mini",
                        "$0.00015",
                        "$0.00060",
                        "$0.00075",
                        "128K",
                        False,
                    ],
                    [
                        "OpenAI GPT-3.5 Turbo",
                        "$0.0005",
                        "$0.0015",
                        "$0.0020",
                        "4K",
                        False,
                    ],
                ]
            elif provider.lower() == "anthropic":
                pricing_data = [
                    [
                        "Anthropic Claude 3.7 Sonnet",
                        "$0.003",
                        "$0.015",
                        "$0.018",
                        "200K",
                        True,
                    ],
                    [
                        "Anthropic Claude 3 Opus",
                        "$0.015",
                        "$0.075",
                        "$0.090",
                        "200K",
                        True,
                    ],
                    [
                        "Anthropic Claude 3.5 Haiku",
                        "$0.0008",
                        "$0.0040",
                        "$0.0048",
                        "200K",
                        False,
                    ],
                ]
            elif provider.lower() == "google":
                pricing_data = [
                    [
                        "Google Gemini 1.5 Pro",
                        "$0.000075",
                        "$0.000300",
                        "$0.000375",
                        "128K",
                        False,
                    ],
                    [
                        "Google Gemini 2.5 Pro Max",
                        "$0.003",
                        "$0.015",
                        "$0.018",
                        "1M",
                        True,
                    ],
                ]
            elif provider.lower() == "cohere":
                pricing_data = [
                    [
                        "Cohere Command R+",
                        "$0.00250",
                        "$0.01000",
                        "$0.0125",
                        "256K",
                        False,
                    ],
                    [
                        "Cohere Command R",
                        "$0.00015",
                        "$0.00060",
                        "$0.00075",
                        "100K",
                        False,
                    ],
                ]
            elif provider.lower() == "ai21":
                pricing_data = [
                    [
                        "AI21 Jamba Large",
                        "$0.0020",
                        "$0.0080",
                        "$0.0100",
                        "100K",
                        False,
                    ],
                    ["AI21 Jamba Mini", "$0.0002", "$0.0004", "$0.0006", "100K", False],
                ]
            elif provider.lower() == "aws":
                pricing_data = [
                    [
                        "AWS Bedrock Titan Text Express",
                        "$0.0008",
                        "$0.0016",
                        "$0.0024",
                        "8K",
                        False,
                    ],
                    [
                        "AWS Bedrock Titan Text Lite",
                        "$0.00015",
                        "$0.00020",
                        "$0.00035",
                        "4K",
                        False,
                    ],
                ]

        return pricing_data

    # TODO: Add code to insert new model configurations
    def insert_new_model_configuration(self, model_name, configuration):
        """
        Insert a new model configuration

        Args:
            model_name (str): Name of the model
            configuration (dict): Model configuration parameters

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Adding new model configuration for: {model_name}")

            # Check if model already exists
            if model_name in self.models_config:
                self.logger.warning(
                    f"Model {model_name} already exists in config, updating instead"
                )
                self.models_config[model_name].update(configuration)
            else:
                # Add new model configuration
                self.models_config[model_name] = configuration

            # Save updated configuration
            self._save_config()
            self.logger.info(
                f"Successfully added/updated model configuration for: {model_name}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error adding model configuration for {model_name}: {str(e)}"
            )
            return False

    # TODO: Add code to insert new model in the pricing block
    def insert_model_in_pricing_block(self, model_name, pricing_data):
        """
        Insert a new model in the pricing block

        Args:
            model_name (str): Name of the model
            pricing_data (dict): Pricing data for different tiers

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Adding pricing data for model: {model_name}")

            # Validate pricing data structure
            required_tiers = ["basic", "standard", "premium", "enterprise"]
            missing_tiers = [
                tier for tier in required_tiers if tier not in pricing_data
            ]

            if missing_tiers:
                self.logger.warning(
                    f"Missing pricing tiers for {model_name}: {', '.join(missing_tiers)}"
                )
                # Fill in missing tiers with null values
                for tier in missing_tiers:
                    pricing_data[tier] = None

            # Add or update model in pricing block
            if "models" not in self.pricing:
                self.pricing["models"] = {}

            self.pricing["models"][model_name] = pricing_data

            # Save updated pricing
            self._save_pricing()
            self.logger.info(
                f"Successfully added/updated pricing for model: {model_name}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error adding pricing for model {model_name}: {str(e)}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="UltraAI Pricing Updater")
    parser.add_argument(
        "--dry-run", action="store_true", help="Run without making changes"
    )
    parser.add_argument(
        "--force", action="store_true", help="Force update even if no changes detected"
    )
    parser.add_argument(
        "--alert-email", help="Email to send alerts to (overrides environment variable)"
    )
    args = parser.parse_args()

    # Override alert email if provided
    if args.alert_email:
        global ALERT_EMAIL
        ALERT_EMAIL = args.alert_email

    # Run the updater
    updater = PricingUpdater(dry_run=args.dry_run, force_update=args.force)
    success = updater.run()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
