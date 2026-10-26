"""Simulation settings. Change REORDER_RULE (or pass --rule) to run the back-test."""

RANDOM_SEED = 42

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"
CLOSED_DAYS = ["2025-04-18", "2025-12-25"]  # Good Friday, Christmas Day

# Ordering
FIRST_ORDER_DATE = "2025-01-06"  # a Monday
ORDER_INTERVAL_DAYS = 14
LEAD_TIME_DAYS = 7
COVERAGE_DAYS = ORDER_INTERVAL_DAYS + LEAD_TIME_DAYS  # 21
SAFETY_STOCK_DAYS = 4  # safety stock = about 4 days of baseline sales

# "as_is": last two weeks of sales + buffer, no pre-promotion top-up
# "to_be": baseline x daily uplift over the coverage period
REORDER_RULE = "as_is"
AS_IS_BUFFER = 0.5  # "a bit extra from experience" on top of last two weeks of sales

# Urgent top-up order (same trigger for both rules, so the comparison is fair):
# closing stock <= safety stock, nothing on order, next regular order more than this many days away
URGENT_MIN_DAYS_TO_NEXT_ORDER = 3

# Baseline
BASELINE_WEEKS = 4
BASELINE_MAX_WEEKS = 8
BASELINE_MIN_WEEKS = 2

# Preset uplift for the first promotion of each type (no history yet)
DEFAULT_UPLIFT = {
    "discount": 1.6,
    "gwp_before": 4.0,
    "gwp_after": 1.4,
}
DEFAULT_GIFT_TAKE_RATE = 0.9  # share of units sold that come with a gift

# Write a few intentional data quality issues into the raw sales file for cleaning practice
MESSY_RAW_DATA = True
