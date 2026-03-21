"""
Cashflow Engine for Secondary Portfolio Underwriting.

Models the full lifecycle of a secondary PE portfolio:
- Capital contributions (drawdowns)
- Distributions (realizations)
- NAV roll-forward with growth assumptions
- Fee drag (management fees, carried interest, fund expenses)
- Net cashflow waterfall
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FundTerms:
    """Fund economic terms for fee modeling."""
    fund_name: str
    vintage_year: int
    fund_size: float  # Total fund commitments
    commitment: float  # LP commitment
    unfunded_commitment: float  # Remaining callable capital
    nav: float  # Current NAV
    management_fee_rate: float = 0.015  # Annual mgmt fee (on committed or invested)
    carried_interest_rate: float = 0.20  # Carry rate
    preferred_return: float = 0.08  # Hurdle rate
    mgmt_fee_basis: str = "committed"  # "committed" or "invested"
    fund_term_years: int = 10  # Original fund term
    years_remaining: int = 5  # Years to full liquidation
    gp_catch_up: float = 1.0  # GP catch-up percentage (1.0 = 100%)


@dataclass
class SecondaryTransaction:
    """A secondary portfolio purchase."""
    fund_terms: FundTerms
    purchase_price: float  # Price paid for the interest
    purchase_date: str  # YYYY-MM-DD
    discount_to_nav: float = 0.0  # Calculated from price vs NAV

    def __post_init__(self):
        if self.fund_terms.nav > 0:
            self.discount_to_nav = 1.0 - (self.purchase_price / self.fund_terms.nav)


@dataclass
class CashflowAssumptions:
    """Assumptions driving the cashflow projection."""
    projection_years: int = 7
    annual_nav_growth_rate: float = 0.08  # Annual NAV appreciation
    contribution_schedule: Optional[list[float]] = None  # % of unfunded called per year
    distribution_pace: Optional[list[float]] = None  # % of beginning NAV distributed per year
    management_fee_step_down_year: Optional[int] = None  # Year mgmt fee steps down
    management_fee_step_down_rate: float = 0.01  # Reduced rate after step-down
    fund_expenses_rate: float = 0.002  # Annual fund-level expenses as % of NAV


class CashflowEngine:
    """
    Core engine for projecting secondary portfolio cashflows.

    Handles:
    1. NAV roll-forward with growth assumptions
    2. Contribution scheduling (unfunded drawdowns)
    3. Distribution pacing (realization timing)
    4. Fee waterfall (mgmt fees, carry, expenses)
    5. Net cashflow to buyer
    """

    def __init__(self, transaction: SecondaryTransaction, assumptions: CashflowAssumptions):
        self.txn = transaction
        self.assumptions = assumptions
        self.fund = transaction.fund_terms
        self._results: Optional[pd.DataFrame] = None

    def _default_contribution_schedule(self) -> list[float]:
        """Default drawdown schedule: front-loaded then tapering."""
        years = self.assumptions.projection_years
        if self.fund.unfunded_commitment <= 0:
            return [0.0] * years
        # Typical pattern: heavy early calls, tapering off
        schedule = []
        remaining = 1.0
        for i in range(years):
            rate = max(0.30 * (0.6 ** i), 0.02) if remaining > 0 else 0.0
            call = min(rate, remaining)
            schedule.append(call)
            remaining -= call
        return schedule

    def _default_distribution_pace(self) -> list[float]:
        """Default distribution pace as % of beginning-period NAV."""
        years = self.assumptions.projection_years
        # Ramp up distributions as fund matures
        pace = []
        for i in range(years):
            if i < 1:
                pace.append(0.10)
            elif i < 3:
                pace.append(0.20 + 0.05 * i)
            else:
                pace.append(min(0.35 + 0.05 * (i - 3), 0.60))
        return pace

    def _calc_management_fees(self, year: int, nav_bop: float, total_committed: float,
                               total_invested: float) -> float:
        """Calculate management fee for a given year."""
        step_down = self.assumptions.management_fee_step_down_year
        if step_down and year >= step_down:
            rate = self.assumptions.management_fee_step_down_rate
        else:
            rate = self.fund.management_fee_rate

        if self.fund.mgmt_fee_basis == "committed":
            return rate * total_committed
        else:  # invested
            return rate * total_invested

    def _calc_carried_interest(self, cumulative_distributions: float,
                                cumulative_contributions: float,
                                cumulative_carry_paid: float) -> float:
        """Calculate carried interest using European-style waterfall."""
        total_invested = cumulative_contributions
        pref_hurdle = total_invested * (1 + self.fund.preferred_return)

        if cumulative_distributions <= pref_hurdle:
            return 0.0

        # Profits above hurdle
        excess = cumulative_distributions - pref_hurdle
        total_carry_owed = excess * self.fund.carried_interest_rate

        # Only pay incremental carry
        incremental = max(0, total_carry_owed - cumulative_carry_paid)
        return incremental

    def project_cashflows(self) -> pd.DataFrame:
        """
        Generate the full cashflow projection.

        Returns a DataFrame with yearly cashflows including:
        - Contributions, Distributions, NAV
        - Management fees, Carried interest, Fund expenses
        - Net cashflow, Cumulative cashflow
        - IRR building blocks
        """
        years = self.assumptions.projection_years
        contrib_schedule = self.assumptions.contribution_schedule or self._default_contribution_schedule()
        dist_pace = self.assumptions.distribution_pace or self._default_distribution_pace()

        # Ensure schedules cover projection period
        contrib_schedule = (contrib_schedule + [0.0] * years)[:years]
        dist_pace = (dist_pace + [dist_pace[-1] if dist_pace else 0.3] * years)[:years]

        rows = []
        nav = self.fund.nav
        unfunded = self.fund.unfunded_commitment
        cumulative_contributions = self.txn.purchase_price  # Includes purchase price
        cumulative_distributions = 0.0
        cumulative_carry_paid = 0.0
        total_committed = self.fund.commitment
        total_invested = self.fund.commitment - self.fund.unfunded_commitment

        for yr in range(years):
            nav_bop = nav

            # --- Contributions (drawdowns) ---
            contribution = unfunded * contrib_schedule[yr]
            unfunded -= contribution
            total_invested += contribution

            # --- NAV Growth ---
            growth = nav_bop * self.assumptions.annual_nav_growth_rate
            nav_after_growth = nav_bop + growth + contribution

            # --- Distributions ---
            distribution = nav_after_growth * dist_pace[yr]
            # In final year, distribute remaining NAV
            if yr == years - 1:
                distribution = max(distribution, nav_after_growth * 0.90)
            nav_after_dist = nav_after_growth - distribution

            # --- Fees ---
            mgmt_fee = self._calc_management_fees(yr, nav_bop, total_committed, total_invested)
            fund_expenses = nav_bop * self.assumptions.fund_expenses_rate

            cumulative_contributions += contribution
            cumulative_distributions += distribution

            carry = self._calc_carried_interest(
                cumulative_distributions, cumulative_contributions, cumulative_carry_paid
            )
            cumulative_carry_paid += carry

            total_fees = mgmt_fee + carry + fund_expenses

            # --- Net cashflow ---
            # From buyer's perspective: contributions are outflows, distributions are inflows
            # Fees reduce distributions
            net_distribution = distribution - total_fees
            net_cashflow = net_distribution - contribution

            # --- NAV end of period (after fees deducted from NAV) ---
            nav_eop = nav_after_dist - total_fees
            nav_eop = max(nav_eop, 0)
            nav = nav_eop

            rows.append({
                "Year": yr + 1,
                "NAV_BOP": round(nav_bop, 2),
                "Contributions": round(contribution, 2),
                "NAV_Growth": round(growth, 2),
                "Gross_Distributions": round(distribution, 2),
                "Management_Fee": round(mgmt_fee, 2),
                "Carried_Interest": round(carry, 2),
                "Fund_Expenses": round(fund_expenses, 2),
                "Total_Fees": round(total_fees, 2),
                "Net_Distributions": round(net_distribution, 2),
                "Net_Cashflow": round(net_cashflow, 2),
                "NAV_EOP": round(nav_eop, 2),
                "Unfunded_Remaining": round(unfunded, 2),
                "Cumulative_Contributions": round(cumulative_contributions, 2),
                "Cumulative_Distributions": round(cumulative_distributions, 2),
            })

        self._results = pd.DataFrame(rows)
        return self._results

    def compute_irr(self) -> Optional[float]:
        """Compute net IRR from the buyer's perspective."""
        if self._results is None:
            self.project_cashflows()

        # Cashflow vector: purchase price (outflow) then yearly net cashflows
        cashflows = [-self.txn.purchase_price]
        for _, row in self._results.iterrows():
            cashflows.append(row["Net_Cashflow"])

        # Add terminal NAV as final inflow
        cashflows[-1] += self._results.iloc[-1]["NAV_EOP"]

        return self._irr(cashflows)

    def compute_moic(self) -> float:
        """Compute multiple on invested capital (MOIC)."""
        if self._results is None:
            self.project_cashflows()

        total_outflows = self.txn.purchase_price + self._results["Contributions"].sum()
        total_inflows = self._results["Net_Distributions"].sum() + self._results.iloc[-1]["NAV_EOP"]

        if total_outflows == 0:
            return 0.0
        return round(total_inflows / total_outflows, 3)

    def compute_dpi(self) -> float:
        """Distributions to Paid-In (DPI) — realized return only."""
        if self._results is None:
            self.project_cashflows()

        total_outflows = self.txn.purchase_price + self._results["Contributions"].sum()
        total_distributions = self._results["Net_Distributions"].sum()

        if total_outflows == 0:
            return 0.0
        return round(total_distributions / total_outflows, 3)

    def compute_tvpi(self) -> float:
        """Total Value to Paid-In (TVPI) = DPI + RVPI."""
        if self._results is None:
            self.project_cashflows()

        total_outflows = self.txn.purchase_price + self._results["Contributions"].sum()
        total_value = self._results["Net_Distributions"].sum() + self._results.iloc[-1]["NAV_EOP"]

        if total_outflows == 0:
            return 0.0
        return round(total_value / total_outflows, 3)

    def get_summary(self) -> dict:
        """Return a summary of key underwriting metrics."""
        if self._results is None:
            self.project_cashflows()

        irr = self.compute_irr()
        return {
            "Fund": self.fund.fund_name,
            "Purchase_Price": self.txn.purchase_price,
            "NAV_at_Purchase": self.fund.nav,
            "Discount_to_NAV": f"{self.txn.discount_to_nav:.1%}",
            "Unfunded_Commitment": self.fund.unfunded_commitment,
            "Net_IRR": f"{irr:.1%}" if irr else "N/A",
            "MOIC": f"{self.compute_moic():.2f}x",
            "DPI": f"{self.compute_dpi():.2f}x",
            "TVPI": f"{self.compute_tvpi():.2f}x",
            "Total_Contributions": self._results["Contributions"].sum(),
            "Total_Net_Distributions": self._results["Net_Distributions"].sum(),
            "Terminal_NAV": self._results.iloc[-1]["NAV_EOP"],
            "Total_Fees_Paid": self._results["Total_Fees"].sum(),
        }

    @staticmethod
    def _irr(cashflows: list[float], guess: float = 0.1, tol: float = 1e-8,
             max_iter: int = 1000) -> Optional[float]:
        """Newton-Raphson IRR solver."""
        rate = guess
        for _ in range(max_iter):
            npv = sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))
            dnpv = sum(-t * cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cashflows))
            if abs(dnpv) < 1e-14:
                return None
            new_rate = rate - npv / dnpv
            if abs(new_rate - rate) < tol:
                return round(new_rate, 6)
            rate = new_rate
        return None


class PortfolioCashflowAggregator:
    """
    Aggregates cashflows across multiple fund positions in a secondary portfolio.
    """

    def __init__(self):
        self.engines: list[CashflowEngine] = []

    def add_position(self, engine: CashflowEngine):
        self.engines.append(engine)

    def aggregate_cashflows(self) -> pd.DataFrame:
        """Combine cashflows from all positions into a single timeline."""
        if not self.engines:
            return pd.DataFrame()

        max_years = max(e.assumptions.projection_years for e in self.engines)
        agg = pd.DataFrame({"Year": range(1, max_years + 1)})

        numeric_cols = [
            "Contributions", "Gross_Distributions", "Net_Distributions",
            "Net_Cashflow", "Management_Fee", "Carried_Interest",
            "Fund_Expenses", "Total_Fees", "NAV_EOP"
        ]
        for col in numeric_cols:
            agg[col] = 0.0

        for engine in self.engines:
            df = engine.project_cashflows()
            for col in numeric_cols:
                if col in df.columns:
                    for _, row in df.iterrows():
                        yr_idx = int(row["Year"]) - 1
                        if yr_idx < len(agg):
                            agg.loc[yr_idx, col] += row[col]

        agg["Cumulative_Net_Cashflow"] = agg["Net_Cashflow"].cumsum()
        return agg

    def portfolio_irr(self) -> Optional[float]:
        """Compute blended portfolio IRR."""
        total_purchase = sum(e.txn.purchase_price for e in self.engines)
        agg = self.aggregate_cashflows()
        if agg.empty:
            return None

        cashflows = [-total_purchase]
        for _, row in agg.iterrows():
            cashflows.append(row["Net_Cashflow"])
        cashflows[-1] += agg.iloc[-1]["NAV_EOP"]

        return CashflowEngine._irr(cashflows)

    def portfolio_moic(self) -> float:
        """Compute blended portfolio MOIC."""
        total_purchase = sum(e.txn.purchase_price for e in self.engines)
        agg = self.aggregate_cashflows()
        if agg.empty or total_purchase == 0:
            return 0.0

        total_outflows = total_purchase + agg["Contributions"].sum()
        total_inflows = agg["Net_Distributions"].sum() + agg.iloc[-1]["NAV_EOP"]
        return round(total_inflows / total_outflows, 3)

    def portfolio_summary(self) -> dict:
        """High-level portfolio metrics."""
        irr = self.portfolio_irr()
        return {
            "Number_of_Funds": len(self.engines),
            "Total_Purchase_Price": sum(e.txn.purchase_price for e in self.engines),
            "Total_NAV": sum(e.fund.nav for e in self.engines),
            "Blended_Discount": f"{1 - sum(e.txn.purchase_price for e in self.engines) / max(sum(e.fund.nav for e in self.engines), 1):.1%}",
            "Total_Unfunded": sum(e.fund.unfunded_commitment for e in self.engines),
            "Portfolio_IRR": f"{irr:.1%}" if irr else "N/A",
            "Portfolio_MOIC": f"{self.portfolio_moic():.2f}x",
        }
