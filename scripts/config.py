"""Simulation settings. Change REORDER_RULE to run the back-test."""

RANDOM_SEED = 42

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"
N_PRODUCTS = 40

# Ordering
ORDER_INTERVAL_DAYS = 14
LEAD_TIME_DAYS = 7
COVERAGE_DAYS = ORDER_INTERVAL_DAYS + LEAD_TIME_DAYS  # 21

# "as_is": last two weeks of sales + buffer, no pre-promotion top-up
# "to_be": baseline x daily uplift over the coverage period
REORDER_RULE = "as_is"

# Preset uplift for the first promotion of each type (no history yet)
DEFAULT_UPLIFT = {
    "discount": 1.8,
    "gwp_before_sellout": 4.5,
    "gwp_after_sellout": 1.5,
}

# Output folders
RAW_DIR = "data/raw"
VALIDATION_DIR = "data/validation"
