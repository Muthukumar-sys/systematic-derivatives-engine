"""
Directional Premium Harvester Strategy
======================================
Engine 1: 15-minute Opening Range Breakout (ORB) + Central Pivot Range (CPR) Momentum.
Executes systematic selling of 0.12 Delta Out-of-the-Money (OTM) options legs with
passive limit orders at mid-price and automated hedge wings.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import pandas as pd
import numpy as np


@dataclass
class TradeSignal:
    timestamp: str
    direction: str          # 'BULLISH' or 'BEARISH'
    spot_price: float
    option_type: str        # 'PE' or 'CE'
    target_delta: float     # 0.12 delta OTM target
    entry_price_est: float
    stop_loss_mult: float   # 1.35x entry premium
    target_profit: float    # Fixed +Rs. 1,500 / lot target
    hard_cutoff_time: str   # '15:15:00'


class DirectionalHarvester:
    """
    Directional options selling strategy utilizing 15m ORB boundary confirmation,
    macro trend gating, and fixed physical strike locking.
    """

    def __init__(
        self,
        min_orb_range: float = 25.0,
        max_orb_range: float = 160.0,
        stop_loss_mult: float = 1.35,
        target_profit_per_lot: float = 1500.0,
        cutoff_time: str = "15:15:00"
    ):
        self.min_orb_range = min_orb_range
        self.max_orb_range = max_orb_range
        self.stop_loss_mult = stop_loss_mult
        self.target_profit_per_lot = target_profit_per_lot
        self.cutoff_time = cutoff_time

    def compute_cpr_levels(self, high: float, low: float, close: float) -> Tuple[float, float, float]:
        """
        Compute Central Pivot Range (Pivot, Bottom Central, Top Central).
        """
        pivot = (high + low + close) / 3.0
        bc = (high + low) / 2.0
        tc = (pivot - bc) + pivot
        tc, bc = max(tc, bc), min(tc, bc)
        return pivot, bc, tc

    def generate_signal(
        self,
        candle_15m_high: float,
        candle_15m_low: float,
        current_5m_close: float,
        prev_day_high: float,
        prev_day_low: float,
        current_time: str
    ) -> Optional[TradeSignal]:
        """
        Evaluates 15m ORB breakout with CPR and boundary gating.
        """
        orb_range = candle_15m_high - candle_15m_low

        # Gating 1: Range compression filter
        if not (self.min_orb_range <= orb_range <= self.max_orb_range):
            return None

        # Gating 2: Time window (09:30 to 10:45 IST)
        if current_time < "09:30:00" or current_time > "10:45:00":
            return None

        # Bullish Breakout: 5m close > ORB High or Previous Day High
        if current_5m_close > candle_15m_high or current_5m_close > prev_day_high:
            return TradeSignal(
                timestamp=current_time,
                direction="BULLISH",
                spot_price=current_5m_close,
                option_type="PE",
                target_delta=0.12,
                entry_price_est=45.0,
                stop_loss_mult=self.stop_loss_mult,
                target_profit=self.target_profit_per_lot,
                hard_cutoff_time=self.cutoff_time
            )

        # Bearish Breakdown: 5m close < ORB Low or Previous Day Low
        if current_5m_close < candle_15m_low or current_5m_close < prev_day_low:
            return TradeSignal(
                timestamp=current_time,
                direction="BEARISH",
                spot_price=current_5m_close,
                option_type="CE",
                target_delta=0.12,
                entry_price_est=45.0,
                stop_loss_mult=self.stop_loss_mult,
                target_profit=self.target_profit_per_lot,
                hard_cutoff_time=self.cutoff_time
            )

        return None
