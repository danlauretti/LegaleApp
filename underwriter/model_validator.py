"""
Model Validator for Secondary Portfolio Underwriting.

Catches formula errors and validates model logic:
- NAV roll-forward consistency checks
- Cashflow balance verification
- Fee calculation sanity checks
- IRR/MOIC cross-validation
- Assumption reasonableness tests
- Data quality flags
"""

import pandas as pd
from dataclasses import dataclass
from typing import Optional

from .cashflow_engine import CashflowEngine, SecondaryTransaction, CashflowAssumptions


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    check_name: str
    passed: bool
    severity: str  # "error", "warning", "info"
    message: str
    details: Optional[dict] = None


class ModelValidator:
    """
    Validates the integrity and reasonableness of a secondary underwriting model.

    Runs a battery of checks on cashflow projections, assumptions, and outputs.
    """

    def __init__(self, engine: CashflowEngine):
        self.engine = engine
        self.txn = engine.txn
        self.assumptions = engine.assumptions
        self.fund = engine.fund
        self.results: list[ValidationResult] = []

    def run_all_checks(self) -> list[ValidationResult]:
        """Run all validation checks and return results."""
        self.results = []

        # Ensure cashflows are projected
        if self.engine._results is None:
            self.engine.project_cashflows()

        df = self.engine._results

        self._check_nav_rollforward(df)
        self._check_cashflow_balance(df)
        self._check_non_negative_nav(df)
        self._check_fee_reasonableness(df)
        self._check_distribution_sanity(df)
        self._check_contribution_sanity(df)
        self._check_irr_moic_consistency()
        self._check_assumption_reasonableness()
        self._check_transaction_pricing()
        self._check_terminal_nav(df)
        self._check_unfunded_drawdown(df)
        self._check_cumulative_monotonicity(df)

        return self.results

    def _add(self, name: str, passed: bool, severity: str, message: str,
             details: Optional[dict] = None):
        self.results.append(ValidationResult(name, passed, severity, message, details))

    # ── NAV Roll-Forward ──────────────────────────────────────────

    def _check_nav_rollforward(self, df: pd.DataFrame):
        """Verify NAV_BOP + Growth + Contributions - Distributions - Fees = NAV_EOP."""
        for _, row in df.iterrows():
            yr = int(row["Year"])
            expected = (row["NAV_BOP"] + row["NAV_Growth"] + row["Contributions"]
                        - row["Gross_Distributions"] - row["Total_Fees"])
            expected = max(expected, 0)
            actual = row["NAV_EOP"]
            diff = abs(expected - actual)

            if diff > 0.01:
                self._add(
                    f"NAV Roll Y{yr}", False, "error",
                    f"Year {yr}: NAV roll mismatch. Expected {expected:.2f}, got {actual:.2f} (diff: {diff:.2f})",
                    {"year": yr, "expected": expected, "actual": actual}
                )
            else:
                self._add(f"NAV Roll Y{yr}", True, "info", f"Year {yr}: NAV roll-forward is consistent.")

    # ── Cashflow Balance ──────────────────────────────────────────

    def _check_cashflow_balance(self, df: pd.DataFrame):
        """Verify Net_Cashflow = Net_Distributions - Contributions."""
        for _, row in df.iterrows():
            yr = int(row["Year"])
            expected = row["Net_Distributions"] - row["Contributions"]
            actual = row["Net_Cashflow"]
            diff = abs(expected - actual)
            if diff > 0.01:
                self._add(
                    f"CF Balance Y{yr}", False, "error",
                    f"Year {yr}: Net cashflow mismatch. Expected {expected:.2f}, got {actual:.2f}",
                )
            else:
                self._add(f"CF Balance Y{yr}", True, "info", f"Year {yr}: Cashflow balance OK.")

    # ── Non-Negative NAV ──────────────────────────────────────────

    def _check_non_negative_nav(self, df: pd.DataFrame):
        """NAV should never go negative."""
        neg_years = df[df["NAV_EOP"] < -0.01]
        if len(neg_years) > 0:
            self._add(
                "Non-Negative NAV", False, "error",
                f"NAV goes negative in years: {neg_years['Year'].tolist()}",
            )
        else:
            self._add("Non-Negative NAV", True, "info", "NAV stays non-negative throughout.")

    # ── Fee Reasonableness ────────────────────────────────────────

    def _check_fee_reasonableness(self, df: pd.DataFrame):
        """Check that fees are reasonable relative to NAV."""
        total_fees = df["Total_Fees"].sum()
        avg_nav = df["NAV_BOP"].mean()
        years = len(df)

        if avg_nav > 0:
            fee_pct = total_fees / (avg_nav * years)
            if fee_pct > 0.05:
                self._add(
                    "Fee Reasonableness", False, "warning",
                    f"Annual fee drag is {fee_pct:.1%} of avg NAV — unusually high.",
                    {"annual_fee_pct": fee_pct}
                )
            elif fee_pct > 0.03:
                self._add(
                    "Fee Reasonableness", True, "warning",
                    f"Annual fee drag is {fee_pct:.1%} of avg NAV — on the high side.",
                )
            else:
                self._add(
                    "Fee Reasonableness", True, "info",
                    f"Annual fee drag is {fee_pct:.1%} of avg NAV — within normal range.",
                )

    # ── Distribution Sanity ───────────────────────────────────────

    def _check_distribution_sanity(self, df: pd.DataFrame):
        """Distributions should not exceed NAV + growth in any period."""
        for _, row in df.iterrows():
            yr = int(row["Year"])
            available = row["NAV_BOP"] + row["NAV_Growth"] + row["Contributions"]
            dist = row["Gross_Distributions"]
            if dist > available * 1.01:  # 1% tolerance
                self._add(
                    f"Dist Sanity Y{yr}", False, "error",
                    f"Year {yr}: Distributions ({dist:.2f}) exceed available NAV ({available:.2f}).",
                )
            else:
                self._add(f"Dist Sanity Y{yr}", True, "info",
                          f"Year {yr}: Distributions within available NAV.")

    # ── Contribution Sanity ───────────────────────────────────────

    def _check_contribution_sanity(self, df: pd.DataFrame):
        """Total contributions should not exceed unfunded commitment."""
        total_contribs = df["Contributions"].sum()
        unfunded = self.fund.unfunded_commitment

        if total_contribs > unfunded * 1.01:
            self._add(
                "Contribution Cap", False, "error",
                f"Total contributions ({total_contribs:.2f}) exceed unfunded commitment ({unfunded:.2f}).",
            )
        else:
            self._add(
                "Contribution Cap", True, "info",
                f"Total contributions ({total_contribs:.2f}) within unfunded ({unfunded:.2f}).",
            )

    # ── IRR / MOIC Cross-Check ────────────────────────────────────

    def _check_irr_moic_consistency(self):
        """IRR and MOIC should be directionally consistent."""
        irr = self.engine.compute_irr()
        moic = self.engine.compute_moic()

        if irr is not None and moic > 0:
            if irr > 0 and moic < 1.0:
                self._add(
                    "IRR/MOIC Consistency", False, "warning",
                    f"IRR is positive ({irr:.1%}) but MOIC is below 1.0x ({moic:.2f}x) — inconsistent.",
                )
            elif irr < 0 and moic > 1.0:
                self._add(
                    "IRR/MOIC Consistency", False, "warning",
                    f"IRR is negative ({irr:.1%}) but MOIC is above 1.0x ({moic:.2f}x) — inconsistent.",
                )
            else:
                self._add(
                    "IRR/MOIC Consistency", True, "info",
                    f"IRR ({irr:.1%}) and MOIC ({moic:.2f}x) are directionally consistent.",
                )
        else:
            self._add(
                "IRR/MOIC Consistency", True, "warning",
                "Could not cross-check IRR/MOIC (IRR did not converge or MOIC is zero).",
            )

    # ── Assumption Reasonableness ─────────────────────────────────

    def _check_assumption_reasonableness(self):
        """Flag unreasonable assumptions."""
        rate = self.assumptions.annual_nav_growth_rate

        if rate > 0.20:
            self._add("Growth Rate", False, "warning",
                       f"NAV growth assumption of {rate:.0%} is very aggressive.")
        elif rate < -0.10:
            self._add("Growth Rate", False, "warning",
                       f"NAV growth assumption of {rate:.0%} is very bearish.")
        else:
            self._add("Growth Rate", True, "info",
                       f"NAV growth assumption of {rate:.0%} is within typical range.")

        if self.assumptions.projection_years > 12:
            self._add("Projection Horizon", False, "warning",
                       f"Projection of {self.assumptions.projection_years} years is unusually long for secondaries.")
        else:
            self._add("Projection Horizon", True, "info",
                       f"Projection horizon of {self.assumptions.projection_years} years is reasonable.")

    # ── Transaction Pricing ───────────────────────────────────────

    def _check_transaction_pricing(self):
        """Validate purchase price relative to NAV."""
        disc = self.txn.discount_to_nav
        if disc < -0.10:
            self._add("Pricing", False, "warning",
                       f"Buying at {disc:.0%} premium to NAV — confirm this is intentional.")
        elif disc > 0.50:
            self._add("Pricing", False, "warning",
                       f"Discount of {disc:.0%} is very steep — verify NAV quality.")
        else:
            self._add("Pricing", True, "info",
                       f"Purchase at {disc:.0%} discount to NAV.")

    # ── Terminal NAV ──────────────────────────────────────────────

    def _check_terminal_nav(self, df: pd.DataFrame):
        """Flag if significant residual NAV remains at end of projection."""
        terminal = df.iloc[-1]["NAV_EOP"]
        initial = df.iloc[0]["NAV_BOP"]
        if initial > 0 and terminal / initial > 0.30:
            self._add(
                "Terminal NAV", True, "warning",
                f"Terminal NAV ({terminal:.0f}) is {terminal/initial:.0%} of initial — "
                f"consider extending projection or adjusting distribution pace.",
            )
        else:
            self._add("Terminal NAV", True, "info",
                       f"Terminal NAV ({terminal:.0f}) is reasonable relative to initial NAV.")

    # ── Unfunded Drawdown Check ───────────────────────────────────

    def _check_unfunded_drawdown(self, df: pd.DataFrame):
        """Check if unfunded gets fully drawn down."""
        final_unfunded = df.iloc[-1]["Unfunded_Remaining"]
        initial_unfunded = self.fund.unfunded_commitment

        if initial_unfunded > 0 and final_unfunded / initial_unfunded > 0.30:
            self._add(
                "Unfunded Utilization", True, "warning",
                f"{final_unfunded:.0f} of {initial_unfunded:.0f} unfunded remains undrawn "
                f"({final_unfunded/initial_unfunded:.0%}) — contribution schedule may be too conservative.",
            )
        else:
            self._add("Unfunded Utilization", True, "info",
                       "Unfunded commitment is sufficiently drawn down.")

    # ── Cumulative Monotonicity ───────────────────────────────────

    def _check_cumulative_monotonicity(self, df: pd.DataFrame):
        """Cumulative contributions and distributions should be monotonically increasing."""
        contribs = df["Cumulative_Contributions"].tolist()
        dists = df["Cumulative_Distributions"].tolist()

        contribs_monotonic = all(contribs[i] >= contribs[i-1] - 0.01 for i in range(1, len(contribs)))
        dists_monotonic = all(dists[i] >= dists[i-1] - 0.01 for i in range(1, len(dists)))

        if not contribs_monotonic:
            self._add("Cumulative Contributions", False, "error",
                       "Cumulative contributions are not monotonically increasing — formula error.")
        else:
            self._add("Cumulative Contributions", True, "info",
                       "Cumulative contributions are monotonically increasing.")

        if not dists_monotonic:
            self._add("Cumulative Distributions", False, "error",
                       "Cumulative distributions are not monotonically increasing — formula error.")
        else:
            self._add("Cumulative Distributions", True, "info",
                       "Cumulative distributions are monotonically increasing.")

    # ── Summary ───────────────────────────────────────────────────

    def summary(self) -> dict:
        """Return a summary of validation results."""
        if not self.results:
            self.run_all_checks()

        errors = [r for r in self.results if not r.passed and r.severity == "error"]
        warnings = [r for r in self.results if not r.passed and r.severity == "warning"]
        passed = [r for r in self.results if r.passed]

        return {
            "total_checks": len(self.results),
            "passed": len(passed),
            "errors": len(errors),
            "warnings": len(warnings),
            "error_details": [{"check": e.check_name, "message": e.message} for e in errors],
            "warning_details": [{"check": w.check_name, "message": w.message} for w in warnings],
            "model_health": "PASS" if len(errors) == 0 else "FAIL",
        }

    def results_dataframe(self) -> pd.DataFrame:
        """Return all validation results as a DataFrame."""
        if not self.results:
            self.run_all_checks()

        rows = []
        for r in self.results:
            rows.append({
                "Check": r.check_name,
                "Status": "PASS" if r.passed else "FAIL",
                "Severity": r.severity.upper(),
                "Message": r.message,
            })
        return pd.DataFrame(rows)
