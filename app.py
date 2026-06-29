import streamlit as st
from config import CONFIG_TABLE, STRATEGY_USES, DATA_PATH
from data_loader import query_data, resolve_config_ids
from sidebar_ui import render_sidebar
from parcoords_component import parcoords_chart

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DC Energy RDM",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state init ───────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "row_count" not in st.session_state:
    st.session_state.row_count = 0
if "last_filters" not in st.session_state:
    st.session_state.last_filters = None

# ── Sidebar ──────────────────────────────────────────────────────────────────
filters = render_sidebar()

# ── On Apply ─────────────────────────────────────────────────────────────────
if filters["apply"]:
    config_ids = resolve_config_ids(
        selected_strategies=filters["selected_strategies"],
        pv_sizes=filters["pv_sizes"],
        wind_sizes=filters["wind_sizes"],
        bess_mwh=filters["bess_mwh"],
        config_table=CONFIG_TABLE,
        strategy_uses=STRATEGY_USES,
    )

    if not config_ids:
        st.error("No configurations match your selections. Adjust the Physical Levers.")
    else:
        df = query_data(
            parquet_path=DATA_PATH,
            location=filters["location"],
            load_profile=filters["load_profile"],
            discount_rate=filters["discount_rate"],
            revenue_structure=filters["revenue_structure"],
            export_excess_re=filters["export_excess_re"],
            config_ids=tuple(sorted(config_ids)),
            lease_rate_min=filters["lease_rate_min"],
            lease_rate_max=filters["lease_rate_max"],
            uncertainty_filters=filters["uncertainty_filters"],
        )
        st.session_state.df = df
        st.session_state.row_count = len(df)
        st.session_state.last_filters = filters

# ── Display ──────────────────────────────────────────────────────────────────
if st.session_state.df is not None:
    df   = st.session_state.df
    n    = st.session_state.row_count
    f    = st.session_state.last_filters

    st.success(f"**{n:,} scenarios** loaded")

    with st.expander("Active filter summary", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Location:** {f['location']}")
            st.markdown(f"**Load Profile:** {f['load_profile']}")
            st.markdown(f"**Discount Rate:** {int(f['discount_rate']*100)}%")
        with col2:
            st.markdown(f"**Revenue Structure:** {f['revenue_structure']}")
            st.markdown(f"**Lease Rate:** £{f['lease_rate_min']:.0f} – £{f['lease_rate_max']:.0f} /kW/mo")
            st.markdown(f"**Export Excess RE:** {f['export_excess_re']}")
        with col3:
            st.markdown(f"**Strategies:** {', '.join(f['selected_strategies'])}")

    # ── Columns to send to D3 ─────────────────────────────────────────────
    PLOT_COLS = [
        "Strategy", "Config_ID", "DC_Lease_Rate",
        "Total_Investment_M", "IRR_pct", "NPV_M",
        "Load_Served_by_RE_pct", "RE_LCOE_per_MWh", "Lifetime_Carbon_tCO2e",
        "DC_Shell_CAPEX", "Solar_PV_CAPEX", "Wind_CAPEX",
        "BESS_Power_CAPEX", "BESS_Energy_CAPEX",
        "Grid_Buy_Price", "Grid_Export_Price", "Grid_Carbon_Intensity",
    ]

    lease_range = f["revenue_structure"]

    payload = {
        "rows":            df[PLOT_COLS].to_dict(orient="records"),
        "irr_min":         0,
        "irr_max":         20,
        "lease_axis_range": [75, 175] if f["revenue_structure"] == "Pass-Through" else [100, 200],
    }

    parcoords_chart(payload=payload, height=720)

else:
    st.markdown(
        """
        <div style='text-align:center; padding: 80px 0; color: #aaa;'>
            <p>Set your filters in the sidebar and click <b>Apply Filters</b>.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )