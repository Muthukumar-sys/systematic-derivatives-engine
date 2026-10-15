"""
Walk-Forward Optimization & In-Sample / Out-of-Sample Partitioning
==================================================================
Partitions chronological datasets into:
- 70% In-Sample (IS): Hypothesis discovery and parameter space tuning.
- 30% Out-of-Sample (OOS): Quarantined validation to test parameter cliff fragility.
"""

from typing import List, Dict, Tuple
import numpy as np
import pandas as pd


class WalkForwardValidator:
    """
    Evaluates strategy parameter stability across non-overlapping
    chronological market windows.
    """

    def __init__(self, in_sample_ratio: float = 0.70):
        self.in_sample_ratio = in_sample_ratio

    def split_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Chronologically splits dataframe without lookahead leakage.
        """
        split_idx = int(len(df) * self.in_sample_ratio)
        df_is = df.iloc[:split_idx].copy()
        df_oos = df.iloc[split_idx:].copy()
        return df_is, df_oos

    def compute_walk_forward_efficiency(
        self,
        is_sharpe: float,
        oos_sharpe: float,
        is_annual_pnl: float,
        oos_annual_pnl: float
    ) -> Dict[str, float]:
        """
        Calculates Walk-Forward Efficiency (WFE) and Sharpe degradation.
        Institutional threshold: WFE >= 0.60 (less than 40% performance decay).
        """
        wfe = (oos_annual_pnl / is_annual_pnl) if is_annual_pnl > 0 else 0.0
        sharpe_decay = (oos_sharpe / is_sharpe) if is_sharpe > 0 else 0.0

        status = "HOLDS UP (ROBUST)" if wfe >= 0.60 and sharpe_decay >= 0.65 else "DEGRADES / FAILS"

        return {
            "is_sharpe": round(is_sharpe, 2),
            "oos_sharpe": round(oos_sharpe, 2),
            "sharpe_retention": round(sharpe_decay, 2),
            "walk_forward_efficiency": round(wfe, 2),
            "status": status
        }


if __name__ == "__main__":
    validator = WalkForwardValidator(in_sample_ratio=0.70)
    print("Testing Walk-Forward Validation Engine...")
    metrics = validator.compute_walk_forward_efficiency(
        is_sharpe=3.62,
        oos_sharpe=3.46,
        is_annual_pnl=182000.0,
        oos_annual_pnl=168000.0
    )
    print("Walk-Forward Efficiency Audit Result:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
