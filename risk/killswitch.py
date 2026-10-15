"""
Risk Killswitch & Capital Defense Governor
==========================================
Enforces non-negotiable risk constraints:
1. Daily Trade Cap (Maximum 1 trade per day per engine)
2. Monthly Loss Killswitch (-2.4% / -Rs. 24,000 max drawdown cap)
3. Hard Intraday Cutoff at 15:15 IST (100% flat cash posture)
"""

from datetime import datetime
from typing import Dict, Any


class RiskGovernor:
    """
    Independent capital defense layer operating ahead of order execution.
    """

    def __init__(
        self,
        account_capital: float = 1000000.0,
        monthly_loss_limit_pct: float = 0.024, # -2.4% max drawdown cap
        hard_cutoff_time: str = "15:15:00"
    ):
        self.account_capital = account_capital
        self.max_monthly_loss = account_capital * monthly_loss_limit_pct
        self.hard_cutoff_time = hard_cutoff_time
        self.monthly_net_pnl = 0.0
        self.daily_trades_executed = 0

    def record_trade_result(self, net_pnl: float):
        """
        Updates cumulative monthly ledger and increments daily trade counter.
        """
        self.monthly_net_pnl += net_pnl
        self.daily_trades_executed += 1

    def can_open_new_trade(self, current_time: str) -> Dict[str, Any]:
        """
        Evaluates risk state against daily limits, monthly cap, and intraday clock.
        """
        # Rule 1: Intraday Time Cutoff
        if current_time >= self.hard_cutoff_time:
            return {
                "allowed": False,
                "reason": f"Time {current_time} exceeds hard 15:15 IST exit threshold"
            }

        # Rule 2: Daily Trade Cap
        if self.daily_trades_executed >= 1:
            return {
                "allowed": False,
                "reason": "Maximum 1 trade per day limit reached"
            }

        # Rule 3: Monthly Killswitch Lock
        if self.monthly_net_pnl <= -self.max_monthly_loss:
            return {
                "allowed": False,
                "reason": f"Monthly loss limit reached: Rs. {self.monthly_net_pnl:.2f} <= -Rs. {self.max_monthly_loss:.2f}"
            }

        return {"allowed": True, "reason": "All risk gates clear"}
