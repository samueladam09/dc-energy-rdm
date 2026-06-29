import os

# ── Data Path ────────────────────────────────────────────────────────────────
DATA_PATH = os.getenv(
    "DATA_PATH",
    r"C:\Users\samue\OneDrive - Imperial College London\Desktop\1- IRP\5- Models\2- Simulation Data\6- Python DCF\20260628_Simulation_Results_Run1.parquet"
)

# ── Config ID Master Table ───────────────────────────────────────────────────
CONFIG_TABLE = [
    ("None", "Grid-Only",         0,   0,   0,   0),
    ("A1",   "Grid-PV",         100,   0,   0,   0),
    ("A2",   "Grid-PV",         150,   0,   0,   0),
    ("A3",   "Grid-PV",         200,   0,   0,   0),
    ("B1",   "Grid-Wind",         0, 100,   0,   0),
    ("B2",   "Grid-Wind",         0, 150,   0,   0),
    ("B3",   "Grid-Wind",         0, 200,   0,   0),
    ("C1",   "Grid-PV-Wind",    100, 100,   0,   0),
    ("C2",   "Grid-PV-Wind",    100, 150,   0,   0),
    ("C3",   "Grid-PV-Wind",    100, 200,   0,   0),
    ("C4",   "Grid-PV-Wind",    150, 100,   0,   0),
    ("C5",   "Grid-PV-Wind",    150, 150,   0,   0),
    ("C6",   "Grid-PV-Wind",    150, 200,   0,   0),
    ("C7",   "Grid-PV-Wind",    200, 100,   0,   0),
    ("C8",   "Grid-PV-Wind",    200, 150,   0,   0),
    ("C9",   "Grid-PV-Wind",    200, 200,   0,   0),
    ("D1",   "Grid-PV-BESS",    100,   0, 100, 200),
    ("D2",   "Grid-PV-BESS",    100,   0, 100, 400),
    ("D3",   "Grid-PV-BESS",    150,   0, 100, 200),
    ("D4",   "Grid-PV-BESS",    150,   0, 100, 400),
    ("D5",   "Grid-PV-BESS",    200,   0, 100, 200),
    ("D6",   "Grid-PV-BESS",    200,   0, 100, 400),
    ("E1",   "Grid-Wind-BESS",    0, 100, 100, 200),
    ("E2",   "Grid-Wind-BESS",    0, 100, 100, 400),
    ("E3",   "Grid-Wind-BESS",    0, 150, 100, 200),
    ("E4",   "Grid-Wind-BESS",    0, 150, 100, 400),
    ("E5",   "Grid-Wind-BESS",    0, 200, 100, 200),
    ("E6",   "Grid-Wind-BESS",    0, 200, 100, 400),
    ("F1",   "Grid-PV-Wind-BESS", 100, 100, 100, 200),
    ("F2",   "Grid-PV-Wind-BESS", 100, 100, 100, 400),
    ("F3",   "Grid-PV-Wind-BESS", 100, 150, 100, 200),
    ("F4",   "Grid-PV-Wind-BESS", 100, 150, 100, 400),
    ("F5",   "Grid-PV-Wind-BESS", 100, 200, 100, 200),
    ("F6",   "Grid-PV-Wind-BESS", 100, 200, 100, 400),
    ("F7",   "Grid-PV-Wind-BESS", 150, 100, 100, 200),
    ("F8",   "Grid-PV-Wind-BESS", 150, 100, 100, 400),
    ("F9",   "Grid-PV-Wind-BESS", 150, 150, 100, 200),
    ("F10",  "Grid-PV-Wind-BESS", 150, 150, 100, 400),
    ("F11",  "Grid-PV-Wind-BESS", 150, 200, 100, 200),
    ("F12",  "Grid-PV-Wind-BESS", 150, 200, 100, 400),
    ("F13",  "Grid-PV-Wind-BESS", 200, 100, 100, 200),
    ("F14",  "Grid-PV-Wind-BESS", 200, 100, 100, 400),
    ("F15",  "Grid-PV-Wind-BESS", 200, 150, 100, 200),
    ("F16",  "Grid-PV-Wind-BESS", 200, 150, 100, 400),
    ("F17",  "Grid-PV-Wind-BESS", 200, 200, 100, 200),
    ("F18",  "Grid-PV-Wind-BESS", 200, 200, 100, 400),
]

# ── Strategy Families ────────────────────────────────────────────────────────
STRATEGY_ORDER = [
    "Grid-Only",
    "Grid-PV",
    "Grid-Wind",
    "Grid-PV-Wind",
    "Grid-PV-BESS",
    "Grid-Wind-BESS",
    "Grid-PV-Wind-BESS",
]

STRATEGY_USES = {
    "Grid-Only":         {"pv": False, "wind": False, "bess": False},
    "Grid-PV":           {"pv": True,  "wind": False, "bess": False},
    "Grid-Wind":         {"pv": False, "wind": True,  "bess": False},
    "Grid-PV-Wind":      {"pv": True,  "wind": True,  "bess": False},
    "Grid-PV-BESS":      {"pv": True,  "wind": False, "bess": True},
    "Grid-Wind-BESS":    {"pv": False, "wind": True,  "bess": True},
    "Grid-PV-Wind-BESS": {"pv": True,  "wind": True,  "bess": True},
}

# ── Lease Rate Ranges by Revenue Structure ───────────────────────────────────
LEASE_RATE_RANGES = {
    "Pass-Through": (75,  175),
    "All-In":       (100, 200),
}

# ── Uncertainty Parameter Ranges ─────────────────────────────────────────────
UNCERTAINTY_RANGES = {
    "DC_Shell_CAPEX":        {"label": "DC Shell CAPEX",        "unit": "£/MW",       "min": 8000,  "max": 12000, "step": 100,  "fmt": ",.0f"},
    "Solar_PV_CAPEX":        {"label": "Solar PV CAPEX",        "unit": "£/MW",       "min": 500,   "max": 850,   "step": 10,   "fmt": ",.0f"},
    "Wind_CAPEX":            {"label": "Wind CAPEX",            "unit": "£/MW",       "min": 1100,  "max": 1800,  "step": 10,   "fmt": ",.0f"},
    "BESS_Power_CAPEX":      {"label": "BESS Power CAPEX",      "unit": "£/MW",       "min": 400,   "max": 750,   "step": 10,   "fmt": ",.0f"},
    "BESS_Energy_CAPEX":     {"label": "BESS Energy CAPEX",     "unit": "£/MWh",      "min": 160,   "max": 280,   "step": 5,    "fmt": ",.0f"},
    "Grid_Buy_Price":        {"label": "Grid Buy Price",        "unit": "£/MWh",      "min": 80,    "max": 150,   "step": 1,    "fmt": ",.0f"},
    "Grid_Export_Price":     {"label": "Grid Export Price",     "unit": "£/MWh",      "min": 40,    "max": 75,    "step": 1,    "fmt": ",.0f"},
    "Grid_Carbon_Intensity": {"label": "Grid Carbon Intensity", "unit": "kgCO₂e/kWh", "min": 0.05,  "max": 0.13,  "step": 0.01, "fmt": ".2f"},
}

# ── Fixed Axis Ranges for Plot ───────────────────────────────────────────────
AXIS_RANGES = {
    "DC_Lease_Rate":         {"Pass-Through": (75, 175),  "All-In": (100, 200)},
    "Total_Investment_M":    (0,    2000),
    "IRR_pct":               (0,    20),
    "NPV_M":                 (-800, 800),
    "Load_Served_by_RE_pct": (0,    100),
    "RE_LCOE_per_MWh":       (0,    500),
    "Lifetime_Carbon_tCO2e": (0,    1_500_000),
}

# ── Discount Rate Float32 Tolerance Map ──────────────────────────────────────
DISCOUNT_RATE_BOUNDS = {
    0.08: (0.079, 0.081),
    0.10: (0.099, 0.101),
    0.12: (0.119, 0.121),
}

# ── Data path resolver — works locally and on Streamlit Cloud ────────────────
def get_data_path() -> str:
    """
    Local dev  → uses the hardcoded OneDrive path directly
    Cloud      → downloads from HuggingFace Hub once, caches in /tmp
    """
    # Local: file exists on disk
    if os.path.exists(DATA_PATH):
        return DATA_PATH

    # Cloud: download from HuggingFace
    try:
        from huggingface_hub import hf_hub_download
        import streamlit as st

        print("Downloading parquet from HuggingFace Hub...")
        local_file = hf_hub_download(
            repo_id   = st.secrets["samueladam09/dc-energy-rdm-data"],
            filename  = st.secrets["20260628_Simulation_Results_Run1.parquet"],
            repo_type = "dataset",
            token     = st.secrets["HF_TOKEN"],
            cache_dir = "/tmp/dc_energy_data",
        )
        print(f"Downloaded to: {local_file}")
        return local_file

    except Exception as e:
        raise FileNotFoundError(
            f"Parquet file not found locally and HuggingFace download failed: {e}"
        )