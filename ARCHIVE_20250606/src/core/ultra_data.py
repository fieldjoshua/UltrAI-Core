import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ultra_base import UltraBase
from ultra_llm import PromptTemplate, RateLimits


@dataclass
class DataConfig:
    """Configuration for data processing and visualization."""

    cache_dir: str = "cache"
    max_cache_age_hours: int = 24
    default_plot_style: str = "seaborn"
    supported_formats: List[str] = None

    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ["csv", "json", "xlsx", "parquet"]


class UltraData(UltraBase):
    def __init__(
        self,
        api_keys: Dict[str, str],
        prompt_templates: Optional[PromptTemplate] = None,
        rate_limits: Optional[RateLimits] = None,
        output_format: str = "plain",
        enabled_features: Optional[List[str]] = None,
    ):
        super().__init__(
            api_keys=api_keys,
            prompt_templates=prompt_templates,
            rate_limits=rate_limits,
            output_format=output_format,
            enabled_features=enabled_features,
        )

    def _initialize_clients(self):
        """Initialize data processing clients."""
        if "pandas" in self.enabled_features:
            print("Pandas initialized for data processing.")
        if "matplotlib" in self.enabled_features:
            print("Matplotlib initialized for visualization.")

    async def process_data(
        self,
        data: Union[pd.DataFrame, np.ndarray, Dict[str, Any]],
        processing_params: Dict[str, Any],
    ) -> pd.DataFrame:
        """Process data according to specified parameters."""
        if not self.is_feature_enabled("pandas"):
            raise ValueError("Pandas feature not enabled")

        try:
            # Convert input to DataFrame if needed
            if isinstance(data, np.ndarray):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame.from_dict(data)
            else:
                df = data.copy()

            # Apply processing parameters
            if "scale" in processing_params:
                df = self._apply_scaling(df, processing_params["scale"])
            if "filter" in processing_params:
                df = self._apply_filtering(df, processing_params["filter"])
            if "transform" in processing_params:
                df = self._apply_transformation(df, processing_params["transform"])

            return df
        except Exception as e:
            self.logger.error(f"Data processing failed: {e}")
            raise

    def _apply_scaling(
        self, df: pd.DataFrame, scale_params: Dict[str, Any]
    ) -> pd.DataFrame:
        """Apply scaling to numeric columns."""
        if scale_params.get("method") == "standard":
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].mean()) / df[
                numeric_cols
            ].std()
        elif scale_params.get("method") == "minmax":
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].min()) / (
                df[numeric_cols].max() - df[numeric_cols].min()
            )
        return df

    def _apply_filtering(
        self, df: pd.DataFrame, filter_params: Dict[str, Any]
    ) -> pd.DataFrame:
        """Apply filtering based on conditions."""
        if "conditions" in filter_params:
            for condition in filter_params["conditions"]:
                df = df.query(condition)
        return df

    def _apply_transformation(
        self, df: pd.DataFrame, transform_params: Dict[str, Any]
    ) -> pd.DataFrame:
        """Apply data transformations."""
        if "groupby" in transform_params:
            groupby_params = transform_params["groupby"]
            df = df.groupby(groupby_params["columns"]).agg(groupby_params["agg"])
        return df

    async def visualize_data(
        self, data: pd.DataFrame, viz_params: Dict[str, Any]
    ) -> str:
        """Create visualizations based on specified parameters."""
        if not self.is_feature_enabled("matplotlib"):
            raise ValueError("Matplotlib feature not enabled")

        try:
            plt.figure(figsize=viz_params.get("figsize", (10, 6)))

            if viz_params.get("type") == "line":
                plt.plot(data.index, data[viz_params["columns"]])
            elif viz_params.get("type") == "bar":
                data[viz_params["columns"]].plot(kind="bar")
            elif viz_params.get("type") == "scatter":
                plt.scatter(data[viz_params["x"]], data[viz_params["y"]])

            # Customize plot
            plt.title(viz_params.get("title", ""))
            plt.xlabel(viz_params.get("xlabel", ""))
            plt.ylabel(viz_params.get("ylabel", ""))

            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"visualization_{timestamp}.png"
            filepath = os.path.join(self.run_dir, filename)
            plt.savefig(filepath)
            plt.close()

            self.logger.info(f"Saved visualization to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Visualization failed: {e}")
            raise
