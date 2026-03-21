"""
Secondary Portfolio Underwriter — Streamlit Application.

A comprehensive tool for underwriting secondary PE portfolio transactions.
"""

import streamlit as st
import pandas as pd
import numpy as np

from underwriter.cashflow_engine import (
    FundTerms, SecondaryTransaction, CashflowAssumptions,
    CashflowEngine, PortfolioCashflowAggregator,
)
from underwriter.portfolio_data import (
    FundPosition, SecondaryPortfolio, PortfolioCompany,
    Strategy, Geography, Sector, load_portfolio_from_csv,
)
from underwriter.scenario_analysis import ScenarioAnalyzer, scenario_results_to_dataframe
from underwriter.model_validator import ModelValidator

# ── Page Config ───────────────────────────────────────────────────

st.set_page_config(
    page_title="Secondary Portfolio Underwriter",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Secondary Portfolio Underwriter")
st.caption("Cashflow modeling, scenario analysis & model validation for PE secondaries")

# ── Sidebar: Portfolio Input ──────────────────────────────────────

st.sidebar.header("Portfolio Setup")

input_mode = st.sidebar.radio(
    "Input Method",
    ["Manual Entry", "CSV Upload", "Sample Portfolio"],
    index=2,
)


def get_sample_portfolio():
    """Generate a realistic sample secondary portfolio."""
    funds = [
        FundTerms("Apex Capital Fund V", 2018, 2_000_000_000, 25_000_000,
                   5_000_000, 32_000_000, 0.015, 0.20, 0.08, "committed", 10, 5),
        FundTerms("Meridian Growth Partners III", 2019, 1_500_000_000, 15_000_000,
                   4_500_000, 18_000_000, 0.020, 0.20, 0.08, "invested", 10, 6),
        FundTerms("Pinnacle Buyout Fund VII", 2017, 3_000_000_000, 30_000_000,
                   2_000_000, 45_000_000, 0.015, 0.20, 0.08, "committed", 10, 4),
        FundTerms("Horizon Ventures II", 2020, 800_000_000, 10_000_000,
                   6_000_000, 11_000_000, 0.020, 0.25, 0.08, "committed", 10, 7),
    ]
    transactions = [
        SecondaryTransaction(funds[0], 27_200_000, "2024-06-30"),  # 15% discount
        SecondaryTransaction(funds[1], 16_200_000, "2024-06-30"),  # 10% discount
        SecondaryTransaction(funds[2], 36_000_000, "2024-06-30"),  # 20% discount
        SecondaryTransaction(funds[3], 10_450_000, "2024-06-30"),  # 5% discount
    ]
    return funds, transactions


def manual_fund_input(idx: int):
    """Render manual input fields for a single fund."""
    st.sidebar.subheader(f"Fund #{idx + 1}")
    name = st.sidebar.text_input(f"Fund Name", f"Fund {idx + 1}", key=f"name_{idx}")
    col1, col2 = st.sidebar.columns(2)
    vintage = col1.number_input("Vintage", 2010, 2026, 2020, key=f"vintage_{idx}")
    fund_size = col2.number_input("Fund Size ($M)", 0.0, 100_000.0, 1_000.0, key=f"fsize_{idx}")
    commitment = st.sidebar.number_input("Your Commitment ($M)", 0.0, 10_000.0, 25.0, key=f"commit_{idx}")
    unfunded = st.sidebar.number_input("Unfunded ($M)", 0.0, 10_000.0, 5.0, key=f"unfunded_{idx}")
    nav = st.sidebar.number_input("Current NAV ($M)", 0.0, 10_000.0, 30.0, key=f"nav_{idx}")
    purchase = st.sidebar.number_input("Purchase Price ($M)", 0.0, 10_000.0, 25.0, key=f"price_{idx}")

    with st.sidebar.expander("Fee Terms"):
        mgmt = st.number_input("Mgmt Fee %", 0.0, 5.0, 1.5, 0.1, key=f"mgmt_{idx}") / 100
        carry = st.number_input("Carry %", 0.0, 50.0, 20.0, 1.0, key=f"carry_{idx}") / 100
        pref = st.number_input("Pref Return %", 0.0, 20.0, 8.0, 0.5, key=f"pref_{idx}") / 100
        basis = st.selectbox("Fee Basis", ["committed", "invested"], key=f"basis_{idx}")

    scale = 1_000_000
    fund = FundTerms(name, vintage, fund_size * scale, commitment * scale,
                      unfunded * scale, nav * scale, mgmt, carry, pref, basis)
    txn = SecondaryTransaction(fund, purchase * scale, "2024-06-30")
    return fund, txn


# ── Build Portfolio ───────────────────────────────────────────────

funds_list = []
txns_list = []

if input_mode == "Sample Portfolio":
    funds_list, txns_list = get_sample_portfolio()
    st.sidebar.success(f"Loaded sample portfolio: {len(funds_list)} funds")

elif input_mode == "Manual Entry":
    num_funds = st.sidebar.number_input("Number of Funds", 1, 20, 2)
    for i in range(int(num_funds)):
        fund, txn = manual_fund_input(i)
        funds_list.append(fund)
        txns_list.append(txn)

elif input_mode == "CSV Upload":
    uploaded = st.sidebar.file_uploader("Upload Portfolio CSV", type=["csv"])
    if uploaded:
        try:
            df_upload = pd.read_csv(uploaded)
            st.sidebar.dataframe(df_upload.head(), use_container_width=True)
            positions = []
            for _, row in df_upload.iterrows():
                d = row.to_dict()
                fund = FundTerms(
                    fund_name=str(d.get("fund_name", "Unknown")),
                    vintage_year=int(d.get("vintage_year", 2020)),
                    fund_size=float(d.get("fund_size", 0)),
                    commitment=float(d.get("commitment", 0)),
                    unfunded_commitment=float(d.get("unfunded_commitment", 0)),
                    nav=float(d.get("nav", 0)),
                    management_fee_rate=float(d.get("management_fee_rate", 0.015)),
                    carried_interest_rate=float(d.get("carried_interest_rate", 0.20)),
                    preferred_return=float(d.get("preferred_return", 0.08)),
                )
                txn = SecondaryTransaction(fund, float(d.get("purchase_price", 0)), "2024-06-30")
                funds_list.append(fund)
                txns_list.append(txn)
            st.sidebar.success(f"Loaded {len(funds_list)} funds from CSV")
        except Exception as e:
            st.sidebar.error(f"Error parsing CSV: {e}")

# ── Sidebar: Assumptions ─────────────────────────────────────────

st.sidebar.header("Cashflow Assumptions")
proj_years = st.sidebar.slider("Projection Years", 3, 12, 7)
nav_growth = st.sidebar.slider("Annual NAV Growth (%)", -10.0, 20.0, 8.0, 0.5) / 100
expense_rate = st.sidebar.slider("Fund Expenses (% of NAV)", 0.0, 1.0, 0.2, 0.05) / 100

assumptions = CashflowAssumptions(
    projection_years=proj_years,
    annual_nav_growth_rate=nav_growth,
    fund_expenses_rate=expense_rate,
)

# ── Main Content ──────────────────────────────────────────────────

if not funds_list:
    st.info("Configure a portfolio using the sidebar to get started.")
    st.stop()

# Build engines
engines = []
for txn in txns_list:
    engine = CashflowEngine(txn, assumptions)
    engine.project_cashflows()
    engines.append(engine)

# ── Tab Layout ────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Portfolio Overview", "Cashflow Model", "Scenario Analysis",
    "Model Validation", "Monte Carlo"
])

# ══════════════════════════════════════════════════════════════════
# TAB 1: Portfolio Overview
# ══════════════════════════════════════════════════════════════════

with tab1:
    st.header("Portfolio Summary")

    # Aggregate metrics
    agg = PortfolioCashflowAggregator()
    for e in engines:
        agg.add_position(e)

    summary = agg.portfolio_summary()

    cols = st.columns(4)
    cols[0].metric("Total Purchase Price", f"${summary['Total_Purchase_Price']:,.0f}")
    cols[1].metric("Total NAV", f"${summary['Total_NAV']:,.0f}")
    cols[2].metric("Blended Discount", summary["Blended_Discount"])
    cols[3].metric("Total Unfunded", f"${summary['Total_Unfunded']:,.0f}")

    cols2 = st.columns(3)
    cols2[0].metric("Portfolio IRR", summary["Portfolio_IRR"])
    cols2[1].metric("Portfolio MOIC", summary["Portfolio_MOIC"])
    cols2[2].metric("Number of Funds", summary["Number_of_Funds"])

    st.subheader("Fund-Level Detail")
    fund_rows = []
    for i, engine in enumerate(engines):
        s = engine.get_summary()
        fund_rows.append({
            "Fund": s["Fund"],
            "Purchase Price": f"${s['Purchase_Price']:,.0f}",
            "NAV": f"${s['NAV_at_Purchase']:,.0f}",
            "Discount": s["Discount_to_NAV"],
            "Unfunded": f"${s['Unfunded_Commitment']:,.0f}",
            "Net IRR": s["Net_IRR"],
            "MOIC": s["MOIC"],
            "DPI": s["DPI"],
            "TVPI": s["TVPI"],
        })
    st.dataframe(pd.DataFrame(fund_rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════
# TAB 2: Cashflow Model
# ══════════════════════════════════════════════════════════════════

with tab2:
    st.header("Cashflow Projections")

    view_mode = st.radio("View", ["Aggregate Portfolio", "Individual Funds"], horizontal=True)

    if view_mode == "Aggregate Portfolio":
        agg_df = agg.aggregate_cashflows()
        st.dataframe(
            agg_df.style.format({
                col: "${:,.0f}" for col in agg_df.columns if col != "Year"
            }),
            use_container_width=True, hide_index=True,
        )

        # Cashflow chart
        st.subheader("Net Cashflow Profile")
        chart_df = agg_df[["Year", "Contributions", "Net_Distributions", "Net_Cashflow"]].copy()
        chart_df["Contributions"] = -chart_df["Contributions"]  # Show as negative
        st.bar_chart(chart_df.set_index("Year")[["Contributions", "Net_Distributions"]])

        st.subheader("NAV Trajectory")
        st.line_chart(agg_df.set_index("Year")["NAV_EOP"])

        st.subheader("Cumulative Net Cashflow")
        st.line_chart(agg_df.set_index("Year")["Cumulative_Net_Cashflow"])

    else:
        fund_selector = st.selectbox(
            "Select Fund",
            [f.fund_name for f in funds_list]
        )
        idx = next(i for i, f in enumerate(funds_list) if f.fund_name == fund_selector)
        engine = engines[idx]
        df = engine._results

        st.dataframe(
            df.style.format({col: "${:,.0f}" for col in df.columns if col != "Year"}),
            use_container_width=True, hide_index=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Net Cashflow")
            st.bar_chart(df.set_index("Year")["Net_Cashflow"])
        with col2:
            st.subheader("NAV Trajectory")
            st.line_chart(df.set_index("Year")["NAV_EOP"])

        st.subheader("Fee Breakdown")
        fee_df = df[["Year", "Management_Fee", "Carried_Interest", "Fund_Expenses"]].copy()
        st.bar_chart(fee_df.set_index("Year"))

# ══════════════════════════════════════════════════════════════════
# TAB 3: Scenario Analysis
# ══════════════════════════════════════════════════════════════════

with tab3:
    st.header("Scenario & Stress Testing")

    scenario_fund = st.selectbox(
        "Run scenarios for",
        [f.fund_name for f in funds_list],
        key="scenario_fund",
    )
    s_idx = next(i for i, f in enumerate(funds_list) if f.fund_name == scenario_fund)
    analyzer = ScenarioAnalyzer(txns_list[s_idx], assumptions)

    scenario_type = st.selectbox("Scenario Type", [
        "NAV Haircuts", "Exit Timing (J-Curve)", "Growth Rate Sensitivity",
        "Discount Sensitivity", "Fee Impact", "2-Way Sensitivity Table",
        "Full Stress Test",
    ])

    if scenario_type == "NAV Haircuts":
        results = analyzer.nav_haircut_scenarios()
        st.dataframe(scenario_results_to_dataframe(results), use_container_width=True, hide_index=True)

    elif scenario_type == "Exit Timing (J-Curve)":
        results = analyzer.exit_timing_scenarios()
        st.dataframe(scenario_results_to_dataframe(results), use_container_width=True, hide_index=True)

    elif scenario_type == "Growth Rate Sensitivity":
        results = analyzer.growth_rate_sensitivity()
        st.dataframe(scenario_results_to_dataframe(results), use_container_width=True, hide_index=True)

    elif scenario_type == "Discount Sensitivity":
        results = analyzer.discount_sensitivity()
        st.dataframe(scenario_results_to_dataframe(results), use_container_width=True, hide_index=True)

    elif scenario_type == "Fee Impact":
        results = analyzer.fee_sensitivity()
        st.dataframe(scenario_results_to_dataframe(results), use_container_width=True, hide_index=True)

    elif scenario_type == "2-Way Sensitivity Table":
        st.subheader("IRR Sensitivity: Discount vs. NAV Growth")
        table = analyzer.two_way_sensitivity()
        st.dataframe(table, use_container_width=True)

    elif scenario_type == "Full Stress Test":
        all_results = analyzer.full_stress_test()
        for category, results in all_results.items():
            st.subheader(category)
            st.dataframe(scenario_results_to_dataframe(results),
                         use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════
# TAB 4: Model Validation
# ══════════════════════════════════════════════════════════════════

with tab4:
    st.header("Model Validation & Error Checking")

    val_fund = st.selectbox(
        "Validate model for",
        [f.fund_name for f in funds_list],
        key="val_fund",
    )
    v_idx = next(i for i, f in enumerate(funds_list) if f.fund_name == val_fund)
    validator = ModelValidator(engines[v_idx])
    validation_results = validator.run_all_checks()
    summary = validator.summary()

    # Health indicator
    if summary["model_health"] == "PASS":
        st.success(f"Model Health: PASS — {summary['passed']}/{summary['total_checks']} checks passed")
    else:
        st.error(f"Model Health: FAIL — {summary['errors']} errors, {summary['warnings']} warnings")

    cols = st.columns(3)
    cols[0].metric("Total Checks", summary["total_checks"])
    cols[1].metric("Errors", summary["errors"])
    cols[2].metric("Warnings", summary["warnings"])

    # Show errors first
    if summary["errors"] > 0:
        st.subheader("Errors")
        for err in summary["error_details"]:
            st.error(f"**{err['check']}**: {err['message']}")

    if summary["warnings"] > 0:
        st.subheader("Warnings")
        for warn in summary["warning_details"]:
            st.warning(f"**{warn['check']}**: {warn['message']}")

    # Full results table
    with st.expander("All Validation Results"):
        st.dataframe(validator.results_dataframe(), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════
# TAB 5: Monte Carlo
# ══════════════════════════════════════════════════════════════════

with tab5:
    st.header("Monte Carlo Simulation")

    mc_fund = st.selectbox(
        "Simulate for",
        [f.fund_name for f in funds_list],
        key="mc_fund",
    )
    mc_idx = next(i for i, f in enumerate(funds_list) if f.fund_name == mc_fund)

    col1, col2, col3 = st.columns(3)
    n_sims = col1.number_input("Simulations", 100, 10_000, 1_000, 100)
    growth_mean = col2.number_input("Growth Mean (%)", -10.0, 30.0, 8.0, 0.5) / 100
    growth_std = col3.number_input("Growth Std Dev (%)", 1.0, 20.0, 6.0, 0.5) / 100

    if st.button("Run Monte Carlo", type="primary"):
        analyzer_mc = ScenarioAnalyzer(txns_list[mc_idx], assumptions)
        with st.spinner("Running simulations..."):
            mc_results = analyzer_mc.monte_carlo(
                n_simulations=int(n_sims),
                growth_mean=growth_mean,
                growth_std=growth_std,
            )

        st.subheader("IRR Distribution")
        cols = st.columns(4)
        cols[0].metric("Mean IRR", f"{mc_results['irr_mean']:.1%}" if mc_results['irr_mean'] else "N/A")
        cols[1].metric("Median IRR", f"{mc_results['irr_median']:.1%}" if mc_results['irr_median'] else "N/A")
        cols[2].metric("5th Percentile", f"{mc_results['irr_p5']:.1%}" if mc_results['irr_p5'] else "N/A")
        cols[3].metric("95th Percentile", f"{mc_results['irr_p95']:.1%}" if mc_results['irr_p95'] else "N/A")

        if mc_results["irr_values"]:
            irr_df = pd.DataFrame({"IRR": mc_results["irr_values"]})
            st.bar_chart(irr_df["IRR"].value_counts(bins=50).sort_index())

        st.subheader("MOIC Distribution")
        cols2 = st.columns(4)
        cols2[0].metric("Mean MOIC", f"{mc_results['moic_mean']:.2f}x")
        cols2[1].metric("Median MOIC", f"{mc_results['moic_median']:.2f}x")
        cols2[2].metric("5th Percentile", f"{mc_results['moic_p5']:.2f}x")
        cols2[3].metric("95th Percentile", f"{mc_results['moic_p95']:.2f}x")

        if mc_results["moic_values"]:
            moic_df = pd.DataFrame({"MOIC": mc_results["moic_values"]})
            st.bar_chart(moic_df["MOIC"].value_counts(bins=50).sort_index())

        st.metric("Convergence Rate", f"{mc_results['convergence_pct']:.1f}%")
