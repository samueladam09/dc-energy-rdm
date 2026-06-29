import duckdb
import pandas as pd
import streamlit as st
from config import DISCOUNT_RATE_BOUNDS


def resolve_config_ids(
    selected_strategies: list[str],
    pv_sizes: list[int],
    wind_sizes: list[int],
    bess_mwh: list[int],
    config_table: list[tuple],
    strategy_uses: dict,
) -> list[str]:
    matched = []
    for cfg_id, strategy, solar, wind, bess_pwr, bess_energy in config_table:
        if strategy not in selected_strategies:
            continue
        uses = strategy_uses[strategy]
        if uses["pv"]   and solar       not in pv_sizes:  continue
        if uses["wind"] and wind        not in wind_sizes: continue
        if uses["bess"] and bess_energy not in bess_mwh:  continue
        matched.append(cfg_id)
    return matched


def query_data(
    parquet_path: str,
    location: str,
    load_profile: str,
    discount_rate: float,
    revenue_structure: str,
    export_excess_re: str,
    config_ids: tuple,
    lease_rate_min: float,
    lease_rate_max: float,
    uncertainty_filters: tuple,
) -> pd.DataFrame:

    dr_lo, dr_hi = DISCOUNT_RATE_BOUNDS[discount_rate]
    cfg_list     = ", ".join(f"'{c}'" for c in config_ids)

    # Grid_Export_Price is always 0 when Export_Excess_RE = 'Off'
    # so skip that filter entirely in that case — it would wipe all Off rows
    unc_clauses = "\n          AND ".join(
        f"{col} BETWEEN {lo} AND {hi}"
        for col, lo, hi in uncertainty_filters
        if not (col == "Grid_Export_Price" and export_excess_re == "Off")
    )

    query = f"""
        SELECT *
        FROM read_parquet('{parquet_path}')
        WHERE Location            = '{location}'
          AND Load_Profile        = '{load_profile}'
          AND Discount_Rate       BETWEEN {dr_lo} AND {dr_hi}
          AND Revenue_Structure   = '{revenue_structure}'
          AND Export_Excess_RE    = '{export_excess_re}'
          AND Config_ID           IN ({cfg_list})
          AND DC_Lease_Rate       BETWEEN {lease_rate_min} AND {lease_rate_max}
          AND IRR_pct             IS NOT NULL
          AND {unc_clauses}
    """

    df = duckdb.query(query).df()
    df["RE_LCOE_per_MWh"] = df["RE_LCOE_per_MWh"].fillna(0)
    return df