"""
Scenario Analysis Engine for Secondary Portfolio Underwriting.

Runs sensitivity and stress analysis across:
- J-curve assumptions (contribution/distribution timing)
- Exit timing scenarios
- NAV haircuts and write-downs
- Fee sensitivity
- Discount sensitivity
- Monte Carlo simulation
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional
from itertools import product

from .cashflow_engine import (
    CashflowEngine, CashflowAssumptions, SecondaryTransaction,
    FundTerms, PortfolioCashflowAggregator
)


@dataclass
class ScenarioResult:
    """Result of a single scenario run."""
    scenario_name: str
    irr: Optional[float]
    moic: float
    dpi: float
    tvpi: float
    total_fees: float
    terminal_nav: float
    parameters: dict


class ScenarioAnalyzer:
    """
    Run scenario analysis on a secondary transaction or portfolio.
    """

    def __init__(self, transaction: SecondaryTransaction,
                 base_assumptions: CashflowAssumptions):
        self.txn = transaction
        self.base = base_assumptions

    def _run_scenario(self, name: str, assumptions: CashflowAssumptions,
                      override_txn: Optional[SecondaryTransaction] = None,
                      params: Optional[dict] = None) -> ScenarioResult:
        """Run a single scenario and return results."""
        txn = override_txn or self.txn
        engine = CashflowEngine(txn, assumptions)
        df = engine.project_cashflows()
        irr = engine.compute_irr()
        return ScenarioResult(
            scenario_name=name,
            irr=irr,
            moic=engine.compute_moic(),
            dpi=engine.compute_dpi(),
            tvpi=engine.compute_tvpi(),
            total_fees=df["Total_Fees"].sum(),
            terminal_nav=df.iloc[-1]["NAV_EOP"],
            parameters=params or {},
        )

    # ── NAV Haircut Scenarios ─────────────────────────────────────

    def nav_haircut_scenarios(self, haircuts: Optional[list[float]] = None) -> list[ScenarioResult]:
        """
        Test sensitivity to NAV write-downs.

        Args:
            haircuts: List of haircut percentages (e.g., [0.0, 0.10, 0.20, 0.30, 0.50])
        """
        if haircuts is None:
            haircuts = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]

        results = []
        for haircut in haircuts:
            adjusted_nav = self.txn.fund_terms.nav * (1 - haircut)
            adjusted_fund = FundTerms(
                fund_name=self.txn.fund_terms.fund_name,
                vintage_year=self.txn.fund_terms.vintage_year,
                fund_size=self.txn.fund_terms.fund_size,
                commitment=self.txn.fund_terms.commitment,
                unfunded_commitment=self.txn.fund_terms.unfunded_commitment,
                nav=adjusted_nav,
                management_fee_rate=self.txn.fund_terms.management_fee_rate,
                carried_interest_rate=self.txn.fund_terms.carried_interest_rate,
                preferred_return=self.txn.fund_terms.preferred_return,
                mgmt_fee_basis=self.txn.fund_terms.mgmt_fee_basis,
                fund_term_years=self.txn.fund_terms.fund_term_years,
                years_remaining=self.txn.fund_terms.years_remaining,
            )
            adjusted_txn = SecondaryTransaction(
                fund_terms=adjusted_fund,
                purchase_price=self.txn.purchase_price,
                purchase_date=self.txn.purchase_date,
            )
            name = f"NAV Haircut {haircut:.0%}"
            result = self._run_scenario(name, self.base, adjusted_txn,
                                         {"nav_haircut": haircut})
            results.append(result)
        return results

    # ── J-Curve / Exit Timing Scenarios ───────────────────────────

    def exit_timing_scenarios(self) -> list[ScenarioResult]:
        """
        Model different distribution timing patterns (J-curve shapes).

        Tests: accelerated exits, base case, delayed exits, very delayed.
        """
        scenarios = {
            "Accelerated Exits": {
                "distribution_pace": [0.15, 0.30, 0.40, 0.50, 0.60, 0.70, 0.90],
                "annual_nav_growth_rate": 0.10,
            },
            "Base Case": {
                "distribution_pace": None,
                "annual_nav_growth_rate": self.base.annual_nav_growth_rate,
            },
            "Delayed Exits": {
                "distribution_pace": [0.05, 0.08, 0.12, 0.20, 0.30, 0.45, 0.80],
                "annual_nav_growth_rate": 0.06,
            },
            "Very Delayed / Zombie": {
                "distribution_pace": [0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.60],
                "annual_nav_growth_rate": 0.03,
            },
        }

        results = []
        for name, params in scenarios.items():
            assumptions = CashflowAssumptions(
                projection_years=self.base.projection_years,
                annual_nav_growth_rate=params["annual_nav_growth_rate"],
                distribution_pace=params["distribution_pace"],
                contribution_schedule=self.base.contribution_schedule,
                fund_expenses_rate=self.base.fund_expenses_rate,
            )
            result = self._run_scenario(name, assumptions, params=params)
            results.append(result)
        return results

    # ── NAV Growth Rate Sensitivity ───────────────────────────────

    def growth_rate_sensitivity(self,
                                 rates: Optional[list[float]] = None) -> list[ScenarioResult]:
        """Test sensitivity to NAV growth rate."""
        if rates is None:
            rates = [-0.10, -0.05, 0.0, 0.03, 0.05, 0.08, 0.10, 0.12, 0.15]

        results = []
        for rate in rates:
            assumptions = CashflowAssumptions(
                projection_years=self.base.projection_years,
                annual_nav_growth_rate=rate,
                contribution_schedule=self.base.contribution_schedule,
                distribution_pace=self.base.distribution_pace,
                fund_expenses_rate=self.base.fund_expenses_rate,
            )
            name = f"NAV Growth {rate:.0%}"
            result = self._run_scenario(name, assumptions, params={"growth_rate": rate})
            results.append(result)
        return results

    # ── Discount Sensitivity ──────────────────────────────────────

    def discount_sensitivity(self,
                              discounts: Optional[list[float]] = None) -> list[ScenarioResult]:
        """Test sensitivity to purchase price / discount to NAV."""
        if discounts is None:
            discounts = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40]

        results = []
        for disc in discounts:
            price = self.txn.fund_terms.nav * (1 - disc)
            adjusted_txn = SecondaryTransaction(
                fund_terms=self.txn.fund_terms,
                purchase_price=price,
                purchase_date=self.txn.purchase_date,
            )
            name = f"Discount {disc:.0%}"
            result = self._run_scenario(name, self.base, adjusted_txn,
                                         {"discount": disc, "price": price})
            results.append(result)
        return results

    # ── Fee Sensitivity ───────────────────────────────────────────

    def fee_sensitivity(self) -> list[ScenarioResult]:
        """Test impact of different fee structures."""
        fee_scenarios = {
            "Low Fees (1.0% / 15%)": (0.010, 0.15),
            "Standard Fees (1.5% / 20%)": (0.015, 0.20),
            "High Fees (2.0% / 20%)": (0.020, 0.20),
            "Premium Fees (2.0% / 25%)": (0.020, 0.25),
        }

        results = []
        for name, (mgmt, carry) in fee_scenarios.items():
            adjusted_fund = FundTerms(
                fund_name=self.txn.fund_terms.fund_name,
                vintage_year=self.txn.fund_terms.vintage_year,
                fund_size=self.txn.fund_terms.fund_size,
                commitment=self.txn.fund_terms.commitment,
                unfunded_commitment=self.txn.fund_terms.unfunded_commitment,
                nav=self.txn.fund_terms.nav,
                management_fee_rate=mgmt,
                carried_interest_rate=carry,
                preferred_return=self.txn.fund_terms.preferred_return,
                mgmt_fee_basis=self.txn.fund_terms.mgmt_fee_basis,
                fund_term_years=self.txn.fund_terms.fund_term_years,
                years_remaining=self.txn.fund_terms.years_remaining,
            )
            adjusted_txn = SecondaryTransaction(
                fund_terms=adjusted_fund,
                purchase_price=self.txn.purchase_price,
                purchase_date=self.txn.purchase_date,
            )
            result = self._run_scenario(name, self.base, adjusted_txn,
                                         {"mgmt_fee": mgmt, "carry": carry})
            results.append(result)
        return results

    # ── Two-Way Sensitivity Table ─────────────────────────────────

    def two_way_sensitivity(self,
                             discounts: Optional[list[float]] = None,
                             growth_rates: Optional[list[float]] = None) -> pd.DataFrame:
        """
        Build a 2D sensitivity table: discount vs. NAV growth rate.
        Returns IRR at each intersection.
        """
        if discounts is None:
            discounts = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
        if growth_rates is None:
            growth_rates = [-0.05, 0.0, 0.05, 0.08, 0.10, 0.15]

        matrix = []
        for disc in discounts:
            row = []
            for rate in growth_rates:
                price = self.txn.fund_terms.nav * (1 - disc)
                txn = SecondaryTransaction(
                    fund_terms=self.txn.fund_terms,
                    purchase_price=price,
                    purchase_date=self.txn.purchase_date,
                )
                assumptions = CashflowAssumptions(
                    projection_years=self.base.projection_years,
                    annual_nav_growth_rate=rate,
                    contribution_schedule=self.base.contribution_schedule,
                    distribution_pace=self.base.distribution_pace,
                    fund_expenses_rate=self.base.fund_expenses_rate,
                )
                engine = CashflowEngine(txn, assumptions)
                engine.project_cashflows()
                irr = engine.compute_irr()
                row.append(f"{irr:.1%}" if irr else "N/A")
            matrix.append(row)

        df = pd.DataFrame(
            matrix,
            index=[f"{d:.0%} Disc" for d in discounts],
            columns=[f"{r:.0%} Growth" for r in growth_rates],
        )
        df.index.name = "Discount \\ Growth"
        return df

    # ── Stress Test Suite ─────────────────────────────────────────

    def full_stress_test(self) -> dict[str, list[ScenarioResult]]:
        """
        Run the complete stress test suite.

        Returns a dictionary of scenario category -> results.
        """
        return {
            "NAV Haircuts": self.nav_haircut_scenarios(),
            "Exit Timing": self.exit_timing_scenarios(),
            "Growth Rate": self.growth_rate_sensitivity(),
            "Discount": self.discount_sensitivity(),
            "Fee Impact": self.fee_sensitivity(),
        }

    # ── Monte Carlo Simulation ────────────────────────────────────

    def monte_carlo(self, n_simulations: int = 1000,
                     growth_mean: float = 0.08,
                     growth_std: float = 0.06,
                     dist_pace_mean: float = 0.25,
                     dist_pace_std: float = 0.08,
                     seed: Optional[int] = 42) -> dict:
        """
        Monte Carlo simulation across randomized assumptions.

        Randomizes NAV growth rate and distribution pace each year.
        Returns distribution of IRR and MOIC outcomes.
        """
        rng = np.random.default_rng(seed)
        irrs = []
        moics = []
        years = self.base.projection_years

        for _ in range(n_simulations):
            # Random growth rate per year
            growth_rate = rng.normal(growth_mean, growth_std)
            # Random distribution pace per year
            dist_pace = [
                max(0.02, min(0.80, rng.normal(dist_pace_mean + 0.03 * yr, dist_pace_std)))
                for yr in range(years)
            ]

            assumptions = CashflowAssumptions(
                projection_years=years,
                annual_nav_growth_rate=growth_rate,
                distribution_pace=dist_pace,
                contribution_schedule=self.base.contribution_schedule,
                fund_expenses_rate=self.base.fund_expenses_rate,
            )
            engine = CashflowEngine(self.txn, assumptions)
            engine.project_cashflows()
            irr = engine.compute_irr()
            moic = engine.compute_moic()

            if irr is not None:
                irrs.append(irr)
            moics.append(moic)

        irr_arr = np.array(irrs)
        moic_arr = np.array(moics)

        return {
            "n_simulations": n_simulations,
            "irr_mean": float(np.mean(irr_arr)) if len(irr_arr) > 0 else None,
            "irr_median": float(np.median(irr_arr)) if len(irr_arr) > 0 else None,
            "irr_std": float(np.std(irr_arr)) if len(irr_arr) > 0 else None,
            "irr_p5": float(np.percentile(irr_arr, 5)) if len(irr_arr) > 0 else None,
            "irr_p25": float(np.percentile(irr_arr, 25)) if len(irr_arr) > 0 else None,
            "irr_p75": float(np.percentile(irr_arr, 75)) if len(irr_arr) > 0 else None,
            "irr_p95": float(np.percentile(irr_arr, 95)) if len(irr_arr) > 0 else None,
            "moic_mean": float(np.mean(moic_arr)),
            "moic_median": float(np.median(moic_arr)),
            "moic_std": float(np.std(moic_arr)),
            "moic_p5": float(np.percentile(moic_arr, 5)),
            "moic_p95": float(np.percentile(moic_arr, 95)),
            "irr_values": irr_arr.tolist(),
            "moic_values": moic_arr.tolist(),
            "convergence_pct": len(irrs) / n_simulations * 100,
        }


def scenario_results_to_dataframe(results: list[ScenarioResult]) -> pd.DataFrame:
    """Convert a list of ScenarioResults to a display-ready DataFrame."""
    rows = []
    for r in results:
        rows.append({
            "Scenario": r.scenario_name,
            "IRR": f"{r.irr:.1%}" if r.irr else "N/A",
            "MOIC": f"{r.moic:.2f}x",
            "DPI": f"{r.dpi:.2f}x",
            "TVPI": f"{r.tvpi:.2f}x",
            "Total Fees": f"{r.total_fees:,.0f}",
            "Terminal NAV": f"{r.terminal_nav:,.0f}",
        })
    return pd.DataFrame(rows)
