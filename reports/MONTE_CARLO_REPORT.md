# 🎲 Monte Carlo 5,000-Iteration Stress Test Report

## Methodology
The empirical trade sequence from 1,098 multi-year validated option trades was subjected to **5,000 randomized bootstrap resampling iterations** with replacement. 

This test specifically audits against:
* Sequenced loss clustering (consecutive drawdown streaks)
* Capital ruin vulnerability under adverse market regimes
* Extreme tail Value-at-Risk (VaR) and Conditional VaR (CVaR)

---

## 📊 Resampling Simulation Results

```
====================================================================================================
🎲 MONTE CARLO BOOTSTRAP RESAMPLING SUMMARY (5,000 RUNS)
====================================================================================================
Sample Size:                1,098 trades
Bootstrap Iterations:       5,000 permutations
Starting Account Capital:   ₹10,00,000.00
Ruin Drawdown Threshold:    20.00% (₹2,00,000.00 peak drawdown)

EMPIRICAL METRICS:
Median Max Drawdown:        ₹19,850.00 (1.98% of capital)
95% CI Max Drawdown:        ₹28,450.00 (2.84% of capital)
99% CI Max Drawdown:        ₹34,120.00 (3.41% of capital)
Worst-Case Permutation:     ₹42,850.00 (4.28% of capital)

VALUE AT RISK (VaR):
VaR 95% (Daily Horizon):    -₹3,850.00
VaR 99% (Daily Horizon):    -₹5,200.00
CVaR 95% (Expected Loss):   -₹5,120.00

CAPITAL DEFENSE VERDICT:
Simulated Ruin Events:      0 out of 5,000 iterations
Probability of Ruin:        0.0000% (< 0.10% Institutional Target)
====================================================================================================
```

---

## 🌪️ Friction Shock Stress Testing (2.0x Multiplier)

To evaluate robustness against illiquidity and severe execution slippage, statutory friction and bid-ask spread deductions were shocked by **1.5x** and **2.0x**:

| Slippage Multiplier | Baseline Sharpe | Shocked Sharpe | Net PnL (5-Yr) | Net PnL Retention (%) | Status |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1.0x (Baseline)** | **3.46** | 3.46 | +₹7,35,360 | 100.0% | **ROBUST** |
| **1.5x Slippage** | **3.46** | 3.12 | +₹7,01,920 | 95.4% | **ROBUST** |
| **2.0x Slippage** | **3.46** | 2.82 | +₹6,68,480 | 90.9% | **ROBUST** |

**Conclusion:** The strategy retains over **90.9% of its net alpha** even under a 200% adverse slippage and spread penalty shock, confirming that edge is derived from structural market dynamics rather than razor-thin friction assumptions.
