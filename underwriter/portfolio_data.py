"""
Portfolio Data Models for Secondary Underwriting.

Structures for organizing data from:
- Confidential Information Memorandums (CIMs)
- Fund quarterly reports
- Public market data
- Portfolio company details
"""

import pandas as pd
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from datetime import date


class Strategy(Enum):
    BUYOUT = "Buyout"
    GROWTH_EQUITY = "Growth Equity"
    VENTURE_CAPITAL = "Venture Capital"
    REAL_ESTATE = "Real Estate"
    INFRASTRUCTURE = "Infrastructure"
    CREDIT = "Credit"
    SECONDARIES = "Secondaries"
    FUND_OF_FUNDS = "Fund of Funds"
    CO_INVEST = "Co-Investment"
    OTHER = "Other"


class Geography(Enum):
    NORTH_AMERICA = "North America"
    EUROPE = "Europe"
    ASIA_PACIFIC = "Asia Pacific"
    GLOBAL = "Global"
    EMERGING_MARKETS = "Emerging Markets"
    OTHER = "Other"


class Sector(Enum):
    TECHNOLOGY = "Technology"
    HEALTHCARE = "Healthcare"
    FINANCIAL_SERVICES = "Financial Services"
    CONSUMER = "Consumer"
    INDUSTRIALS = "Industrials"
    ENERGY = "Energy"
    REAL_ESTATE = "Real Estate"
    TELECOM = "Telecom"
    MATERIALS = "Materials"
    DIVERSIFIED = "Diversified"
    OTHER = "Other"


@dataclass
class PortfolioCompany:
    """Individual portfolio company within a fund."""
    name: str
    sector: Sector = Sector.OTHER
    geography: Geography = Geography.NORTH_AMERICA
    investment_date: Optional[str] = None  # YYYY-MM-DD
    cost_basis: float = 0.0  # Total invested cost
    current_fair_value: float = 0.0  # Current FMV / NAV
    revenue: float = 0.0  # LTM revenue
    ebitda: float = 0.0  # LTM EBITDA
    net_debt: float = 0.0  # Net debt
    enterprise_value: float = 0.0  # Current EV
    ownership_pct: float = 0.0  # Fund's ownership %
    entry_multiple: float = 0.0  # EV/EBITDA at entry
    current_multiple: float = 0.0  # Current EV/EBITDA
    revenue_growth_rate: float = 0.0  # YoY revenue growth
    ebitda_margin: float = 0.0  # EBITDA margin
    notes: str = ""

    @property
    def moic(self) -> float:
        if self.cost_basis == 0:
            return 0.0
        return round(self.current_fair_value / self.cost_basis, 2)

    @property
    def unrealized_gain(self) -> float:
        return self.current_fair_value - self.cost_basis

    @property
    def leverage_ratio(self) -> float:
        if self.ebitda == 0:
            return 0.0
        return round(self.net_debt / self.ebitda, 1)


@dataclass
class FundPosition:
    """A single fund position in a secondary portfolio."""
    fund_name: str
    gp_name: str
    strategy: Strategy = Strategy.BUYOUT
    geography: Geography = Geography.NORTH_AMERICA
    vintage_year: int = 2020
    fund_size: float = 0.0
    commitment: float = 0.0
    funded_to_date: float = 0.0
    unfunded_commitment: float = 0.0
    nav: float = 0.0
    total_distributions: float = 0.0
    dpi: float = 0.0
    tvpi: float = 0.0
    irr_net: Optional[float] = None  # Net IRR to LPs
    num_portfolio_companies: int = 0
    top_holdings: list[PortfolioCompany] = field(default_factory=list)
    last_report_date: Optional[str] = None
    fund_term_expiry: Optional[str] = None
    notes: str = ""

    @property
    def funded_pct(self) -> float:
        if self.commitment == 0:
            return 0.0
        return round(self.funded_to_date / self.commitment, 3)

    @property
    def remaining_value(self) -> float:
        return self.nav

    def add_company(self, company: PortfolioCompany):
        self.top_holdings.append(company)

    def concentration_by_sector(self) -> dict[str, float]:
        """Portfolio concentration by sector based on FMV."""
        total_fmv = sum(c.current_fair_value for c in self.top_holdings)
        if total_fmv == 0:
            return {}
        return {
            c.sector.value: round(c.current_fair_value / total_fmv, 3)
            for c in self.top_holdings
        }

    def top_holdings_table(self) -> pd.DataFrame:
        """Return top holdings as a DataFrame for display."""
        if not self.top_holdings:
            return pd.DataFrame()
        rows = []
        for c in sorted(self.top_holdings, key=lambda x: x.current_fair_value, reverse=True):
            rows.append({
                "Company": c.name,
                "Sector": c.sector.value,
                "Cost": c.cost_basis,
                "Fair Value": c.current_fair_value,
                "MOIC": f"{c.moic:.1f}x",
                "EV/EBITDA": f"{c.current_multiple:.1f}x" if c.current_multiple else "N/A",
                "Revenue Growth": f"{c.revenue_growth_rate:.0%}" if c.revenue_growth_rate else "N/A",
                "EBITDA Margin": f"{c.ebitda_margin:.0%}" if c.ebitda_margin else "N/A",
                "Leverage": f"{c.leverage_ratio:.1f}x" if c.leverage_ratio else "N/A",
            })
        return pd.DataFrame(rows)


@dataclass
class SecondaryPortfolio:
    """Complete secondary portfolio being underwritten."""
    portfolio_name: str
    seller_name: str = ""
    transaction_date: Optional[str] = None
    positions: list[FundPosition] = field(default_factory=list)

    def add_position(self, position: FundPosition):
        self.positions.append(position)

    @property
    def total_nav(self) -> float:
        return sum(p.nav for p in self.positions)

    @property
    def total_unfunded(self) -> float:
        return sum(p.unfunded_commitment for p in self.positions)

    @property
    def total_commitments(self) -> float:
        return sum(p.commitment for p in self.positions)

    @property
    def num_funds(self) -> int:
        return len(self.positions)

    @property
    def weighted_avg_vintage(self) -> float:
        total_nav = self.total_nav
        if total_nav == 0:
            return 0
        return round(sum(p.vintage_year * p.nav for p in self.positions) / total_nav, 1)

    def strategy_breakdown(self) -> dict[str, float]:
        """NAV-weighted strategy allocation."""
        total_nav = self.total_nav
        if total_nav == 0:
            return {}
        breakdown: dict[str, float] = {}
        for p in self.positions:
            key = p.strategy.value
            breakdown[key] = breakdown.get(key, 0) + p.nav
        return {k: round(v / total_nav, 3) for k, v in breakdown.items()}

    def geography_breakdown(self) -> dict[str, float]:
        """NAV-weighted geography allocation."""
        total_nav = self.total_nav
        if total_nav == 0:
            return {}
        breakdown: dict[str, float] = {}
        for p in self.positions:
            key = p.geography.value
            breakdown[key] = breakdown.get(key, 0) + p.nav
        return {k: round(v / total_nav, 3) for k, v in breakdown.items()}

    def vintage_breakdown(self) -> dict[int, float]:
        """NAV-weighted vintage year allocation."""
        total_nav = self.total_nav
        if total_nav == 0:
            return {}
        breakdown: dict[int, float] = {}
        for p in self.positions:
            breakdown[p.vintage_year] = breakdown.get(p.vintage_year, 0) + p.nav
        return {k: round(v / total_nav, 3) for k, v in sorted(breakdown.items())}

    def summary_table(self) -> pd.DataFrame:
        """Summary table of all positions."""
        rows = []
        for p in self.positions:
            rows.append({
                "Fund": p.fund_name,
                "GP": p.gp_name,
                "Strategy": p.strategy.value,
                "Vintage": p.vintage_year,
                "Commitment": p.commitment,
                "Funded %": f"{p.funded_pct:.0%}",
                "NAV": p.nav,
                "Unfunded": p.unfunded_commitment,
                "DPI": f"{p.dpi:.2f}x",
                "TVPI": f"{p.tvpi:.2f}x",
                "Net IRR": f"{p.irr_net:.1%}" if p.irr_net else "N/A",
                "# Companies": p.num_portfolio_companies,
            })
        return pd.DataFrame(rows)


def parse_fund_data_from_dict(data: dict) -> FundPosition:
    """
    Parse a fund position from a dictionary (e.g., from JSON/CSV import).

    Expected keys match FundPosition fields. Unknown keys are ignored.
    """
    strategy = Strategy.BUYOUT
    for s in Strategy:
        if s.value.lower() == str(data.get("strategy", "")).lower():
            strategy = s
            break

    geography = Geography.NORTH_AMERICA
    for g in Geography:
        if g.value.lower() == str(data.get("geography", "")).lower():
            geography = g
            break

    return FundPosition(
        fund_name=data.get("fund_name", "Unknown Fund"),
        gp_name=data.get("gp_name", "Unknown GP"),
        strategy=strategy,
        geography=geography,
        vintage_year=int(data.get("vintage_year", 2020)),
        fund_size=float(data.get("fund_size", 0)),
        commitment=float(data.get("commitment", 0)),
        funded_to_date=float(data.get("funded_to_date", 0)),
        unfunded_commitment=float(data.get("unfunded_commitment", 0)),
        nav=float(data.get("nav", 0)),
        total_distributions=float(data.get("total_distributions", 0)),
        dpi=float(data.get("dpi", 0)),
        tvpi=float(data.get("tvpi", 0)),
        irr_net=float(data.get("irr_net")) if data.get("irr_net") else None,
        num_portfolio_companies=int(data.get("num_portfolio_companies", 0)),
        last_report_date=data.get("last_report_date"),
        notes=data.get("notes", ""),
    )


def load_portfolio_from_csv(filepath: str) -> list[FundPosition]:
    """Load fund positions from a CSV file."""
    df = pd.read_csv(filepath)
    positions = []
    for _, row in df.iterrows():
        positions.append(parse_fund_data_from_dict(row.to_dict()))
    return positions


def load_portfolio_from_excel(filepath: str, sheet_name: str = "Portfolio") -> list[FundPosition]:
    """Load fund positions from an Excel file."""
    df = pd.read_excel(filepath, sheet_name=sheet_name)
    positions = []
    for _, row in df.iterrows():
        positions.append(parse_fund_data_from_dict(row.to_dict()))
    return positions
