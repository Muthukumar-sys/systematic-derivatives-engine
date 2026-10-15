"""
Morning Volatility Strangle Strategy
====================================
Engine 2: Far-OTM Strangle Seller deployed at 09:20 AM.
Captures opening implied volatility (IV) crush and structural theta decay
with 80% decay capture profit target and strict leg-wise stop loss.
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class StranglePosition:
    call_strike: float
    put_strike: float
    call_entry_price: float
    put_entry_price: float
    total_credit: float
    target_credit_exit: float   # 80% decay capture (exit at 20% of credit)
    max_loss_per_leg: float     # 1.50x individual leg premium


class MorningStrangleHarvester:
    """
    Non-directional morning theta harvesting engine.
    Trades strictly on non-event, low-to-medium IV days.
    """

    def __init__(
        self,
        strike_distance_pts: float = 400.0,
        decay_target_pct: float = 0.80,
        leg_stop_loss_mult: float = 1.50,
        entry_time: str = "09:20:00",
        exit_cutoff_time: str = "15:15:00"
    ):
        self.strike_distance_pts = strike_distance_pts
        self.decay_target_pct = decay_target_pct
        self.leg_stop_loss_mult = leg_stop_loss_mult
        self.entry_time = entry_time
        self.exit_cutoff_time = exit_cutoff_time

    def select_strikes(self, spot_price: float) -> Tuple[float, float]:
        """
        Determines the Call and Put strikes based on fixed 400pt wings from ATM spot.
        """
        atm_strike = round(spot_price / 50.0) * 50.0
        call_strike = atm_strike + self.strike_distance_pts
        put_strike = atm_strike - self.strike_distance_pts
        return call_strike, put_strike

    def initialize_position(
        self,
        call_strike: float,
        put_strike: float,
        call_ltp: float,
        put_ltp: float
    ) -> StranglePosition:
        """
        Initializes the strangle basket with defined profit target and leg SLs.
        """
        total_credit = call_ltp + put_ltp
        target_exit = total_credit * (1.0 - self.decay_target_pct)

        return StranglePosition(
            call_strike=call_strike,
            put_strike=put_strike,
            call_entry_price=call_ltp,
            put_entry_price=put_ltp,
            total_credit=total_credit,
            target_credit_exit=target_exit,
            max_loss_per_leg=self.leg_stop_loss_mult
        )
