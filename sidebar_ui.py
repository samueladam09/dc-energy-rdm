import streamlit as st
from config import (
    STRATEGY_ORDER,
    STRATEGY_USES,
    LEASE_RATE_RANGES,
    UNCERTAINTY_RANGES,
    CONFIG_TABLE,
)


def render_sidebar() -> dict:
    """
    Renders the full sidebar UI and returns a filters dict.
    """

    # ── Tighter spacing via CSS ──────────────────────────────────────────────
    st.markdown("""
        <style>
            /* Tighten gap between sidebar widgets */
            [data-testid="stSidebar"] .block-container {padding-top: 0.2rem;}
            [data-testid="stSidebar"] .stRadio,
            [data-testid="stSidebar"] .stCheckbox,
            [data-testid="stSidebar"] .stSlider {
                margin-bottom: -8px;
            }
            [data-testid="stSidebar"] .stMarkdown p {
                margin-bottom: 2px;
                margin-top: 6px;
            }
            [data-testid="stSidebar"] hr {
                margin: 6px 0;
            }
            /* Section headers */
            [data-testid="stSidebar"] h3 {
                margin-top: 8px;
                margin-bottom: 2px;
                font-size: 0.95rem;
                font-weight: 700;
                color: #1E293B;
            }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("DC Energy RDM v1")

    # ── Section 1: Inputs ────────────────────────────────────────────────────
    st.sidebar.markdown("### Inputs")

    location = st.sidebar.radio(
        "Location",
        options=["SE", "NE", "SC"],
        format_func=lambda x: {
            "SE": "South East",
            "NE": "North East",
            "SC": "Scotland",
        }[x],
        horizontal=True,
    )

    load_profile = st.sidebar.radio(
        "Load Profile",
        options=["Low_40", "Mid_60", "High_80"],
        format_func=lambda x: {
            "Low_40": "Low (40%)",
            "Mid_60": "Mid (60%)",
            "High_80": "High (80%)",
        }[x],
        horizontal=True,
    )

    discount_rate = st.sidebar.radio(
        "Discount Rate",
        options=[0.08, 0.10, 0.12],
        format_func=lambda x: f"{int(x * 100)}%",
        horizontal=True,
    )

    st.sidebar.divider()

    # ── Section 2: Physical Levers ───────────────────────────────────────────
    st.sidebar.markdown("### Physical Levers")
    st.sidebar.markdown("**Strategy**")

    selected_strategies = []
    for strategy in STRATEGY_ORDER:
        default = strategy in ("Grid-Only", "Grid-PV")
        checked = st.sidebar.checkbox(
            strategy,
            value=default,
            key=f"strat_{strategy}",
        )
        if checked:
            selected_strategies.append(strategy)

    # Determine which components are needed
    needs_pv   = any(STRATEGY_USES[s]["pv"]   for s in selected_strategies)
    needs_wind = any(STRATEGY_USES[s]["wind"] for s in selected_strategies)
    needs_bess = any(STRATEGY_USES[s]["bess"] for s in selected_strategies)

    # PV sizes
    pv_sizes = []
    if needs_pv:
        st.sidebar.markdown("**Solar PV Size (MW)**")
        for mw in [100, 150, 200]:
            if st.sidebar.checkbox(
                f"{mw} MW",
                value=(mw == 100),
                key=f"pv_{mw}",
            ):
                pv_sizes.append(mw)
    else:
        pv_sizes = [100, 150, 200]

    # Wind sizes
    wind_sizes = []
    if needs_wind:
        st.sidebar.markdown("**Wind Size (MW)**")
        for mw in [100, 150, 200]:
            if st.sidebar.checkbox(
                f"{mw} MW",
                value=(mw == 100),
                key=f"wind_{mw}",
            ):
                wind_sizes.append(mw)
    else:
        wind_sizes = [100, 150, 200]

    # BESS MWh
    bess_mwh = []
    if needs_bess:
        st.sidebar.markdown("**BESS Energy (MWh)**")
        for mwh in [200, 400]:
            if st.sidebar.checkbox(
                f"{mwh} MWh",
                value=(mwh == 200),
                key=f"bess_{mwh}",
            ):
                bess_mwh.append(mwh)
    else:
        bess_mwh = [200, 400]

    st.sidebar.divider()

    # ── Section 3: Commercial Levers ─────────────────────────────────────────
    st.sidebar.markdown("### Commercial Levers")

    revenue_structure = st.sidebar.radio(
        "Revenue Structure",
        options=["Pass-Through", "All-In"],
        horizontal=True,
    )

    lease_min, lease_max = LEASE_RATE_RANGES[revenue_structure]
    slider_key = f"lease_slider_{revenue_structure}"
    lease_range = st.sidebar.slider(
        "Lease Rate (£/kW/month)",
        min_value=lease_min,
        max_value=lease_max,
        value=(lease_min, lease_max),
        step=1,
        format="%d",
        key=slider_key,
    )

    export_excess_re = st.sidebar.radio(
        "Export Excess RE",
        options=["On", "Off"],
        horizontal=True,
    )

    st.sidebar.divider()

    # ── Section 4: Uncertainties ─────────────────────────────────────────────
    st.sidebar.markdown("### Uncertainties")

    uncertainty_filters = []
    for col, meta in UNCERTAINTY_RANGES.items():
        p_min  = meta["min"]
        p_max  = meta["max"]
        p_step = meta["step"]

        # Format string — integers for step >= 1, two decimals for small steps
        fmt = "%d" if p_step >= 1 else "%.2f"

        val = st.sidebar.slider(
            f"{meta['label']} ({meta['unit']})",
            min_value=p_min,
            max_value=p_max,
            value=(p_min, p_max),
            step=p_step,
            format=fmt,
            key=f"unc_slider_{col}",
        )
        uncertainty_filters.append((col, val[0], val[1]))

    st.sidebar.divider()

    # ── Apply + Validation ───────────────────────────────────────────────────
    apply = st.sidebar.button(
        "Apply Filters",
        type="primary",
        use_container_width=True,
    )

    warnings = []
    if not selected_strategies:
        warnings.append("Select at least one strategy.")
    if needs_pv and not pv_sizes:
        warnings.append("Select at least one PV size.")
    if needs_wind and not wind_sizes:
        warnings.append("Select at least one Wind size.")
    if needs_bess and not bess_mwh:
        warnings.append("Select at least one BESS energy size.")

    for w in warnings:
        st.sidebar.warning(w)

    if warnings:
        apply = False

    return {
        "apply":               apply,
        "location":            location,
        "load_profile":        load_profile,
        "discount_rate":       discount_rate,
        "selected_strategies": selected_strategies,
        "pv_sizes":            pv_sizes,
        "wind_sizes":          wind_sizes,
        "bess_mwh":            bess_mwh,
        "revenue_structure":   revenue_structure,
        "lease_rate_min":      lease_range[0],
        "lease_rate_max":      lease_range[1],
        "export_excess_re":    export_excess_re,
        "uncertainty_filters": tuple(uncertainty_filters),
    }