"""
Realistic Backtesting Engine for Derivatives
=============================================
Enforces institutional execution realism:
1. Pessimistic Intra-Bar Execution (SL-First Rule)
2. Next-Bar Open Fill (T+1 Latency Modeling)
3. Explicit Bid-Ask Spread Friction Deduction
4. Statutory NFO Taxes & Exchange Turnover Modeling
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import numpy as np
import pandas as pd


@dataclass
class TradeResult:
    entry_time: str
    exit_time: str
    symbol: str
    action: str
    entry_price: float
    exit_price: float
    quantity: int
    gross_pnl: float
    taxes_and_friction: float
    net_pnl: float
    exit_reason: str


class RealisticBacktestEngine:
    """
    Simulates live execution conditions with conservative latency,
    adverse spread penalties, and pessimistic order fills.
    """

    def __init__(
        self,
        spread_penalty_per_contract: float = 1.25,
        statutory_tax_rate: float = 0.00062, # STT + Stamp + GST + Turnover
        lots: int = 3,
        lot_size: int = 65                   # Standard 195 quantity
    ):
        self.spread_penalty = spread_penalty_per_contract
        self.tax_rate = statutory_tax_rate
        self.quantity = lots * lot_size

    def simulate_trade(
        self,
        entry_candle: Dict[str, Any],
        subsequent_candles: List[Dict[str, Any]],
        target_profit_pts: float,
        stop_loss_mult: float,
        is_seller: bool = True
    ) -> TradeResult:
        """
        Executes trade with next-bar open fill and pessimistic intra-bar SL-first logic.
        """
        # T+1 Next-Bar Open execution
        base_entry = entry_candle["open"]
        entry_price = base_entry - self.spread_penalty if is_seller else base_entry + self.spread_penalty

        stop_loss_price = entry_price * stop_loss_mult
        target_price = max(0.05, entry_price - target_profit_pts)

        exit_price = None
        exit_time = None
        exit_reason = None

        for candle in subsequent_candles:
            time_str = candle["time"]
            high = candle["high"]
            low = candle["low"]

            # Intra-Bar SL-First Rule: If high touches SL and low touches Target, SL hits first!
            hit_sl = high >= stop_loss_price
            hit_target = low <= target_price

            if hit_sl and hit_target:
                # Pessimistic resolution: Assume adverse excursion occurred first
                exit_price = stop_loss_price + self.spread_penalty
                exit_time = time_str
                exit_reason = "STOP_LOSS_PESSIMISTIC"
                break
            elif hit_sl:
                exit_price = stop_loss_price + self.spread_penalty
                exit_time = time_str
                exit_reason = "STOP_LOSS"
                break
            elif hit_target:
                exit_price = target_price + self.spread_penalty
                exit_time = time_str
                exit_reason = "TARGET_PROFIT"
                break

            # Hard 15:15 IST Cutoff
            if time_str >= "15:15:00":
                exit_price = candle["close"] + self.spread_penalty
                exit_time = time_str
                exit_reason = "EOD_HARD_EXIT"
                break

        if exit_price is None and subsequent_candles:
            last = subsequent_candles[-1]
            exit_price = last["close"] + self.spread_penalty
            exit_time = last["time"]
            exit_reason = "EOD_FALLBACK"

        # PnL computation
        pts_diff = entry_price - exit_price if is_seller else exit_price - entry_price
        gross_pnl = pts_diff * self.quantity
        turnover = (entry_price + exit_price) * self.quantity
        taxes = turnover * self.tax_rate
        net_pnl = gross_pnl - taxes

        return TradeResult(
            entry_time=entry_candle["time"],
            exit_time=exit_time,
            symbol="NIFTY_OPT",
            action="SELL" if is_seller else "BUY",
            entry_price=round(entry_price, 2),
            exit_price=round(exit_price, 2),
            quantity=self.quantity,
            gross_pnl=round(gross_pnl, 2),
            taxes_and_friction=round(taxes, 2),
            net_pnl=round(net_pnl, 2),
            exit_reason=exit_reason
        )
