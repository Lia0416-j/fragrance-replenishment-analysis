"""
Simulate 12 months of data for a fragrance counter.

The simulation runs day by day and product by product, so sales can never be
higher than the stock on hand. Stockouts happen naturally, and demand that
could not be met is saved only to data/validation/true_demand.csv.

Deliveries come from a reorder rule. The rule can be switched, which is how
the back-test works: same demand, only the reorder rule changes.

Usage:
    python scripts/generate_data.py                      # as-is rule, writes to data/
    python scripts/generate_data.py --rule to_be --out output/to_be --clean
"""

import argparse
import json
import math
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import config as C

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Master data (all brands and product names are fictional)
# ---------------------------------------------------------------------------

BRANDS = [
    ("Maison Aurel", ["Women", "Unisex"]),
    ("Lumiere Noire", ["Women"]),
    ("Atelier Sol", ["Unisex"]),
    ("Nordvik", ["Men"]),
    ("Rosaline", ["Women"]),
    ("Oud Republic", ["Men", "Unisex"]),
    ("Blanc Studio", ["Unisex", "Women"]),
    ("Verdant & Co", ["Women", "Men"]),
]

SCENTS = [
    "Velvet Fig", "Amber Dusk", "Sea Salt Neroli", "White Tea", "Cedar Smoke",
    "Rose Atlas", "Midnight Iris", "Golden Vetiver", "Pink Pepper", "Bergamot Rain",
    "Oud Ember", "Linen Musk", "Blue Cypress", "Peony Silk", "Tobacco Leaf",
    "Citrus Grove", "Saffron Veil", "Night Jasmine", "Sandal Bloom", "Coastal Sage",
    "Vanilla Wood", "Iris Powder", "Fig Leaf", "Mandarin Spark", "Smoked Birch",
    "Lavender Field", "Tonka Cream", "Cassis Rose", "Green Vetiver", "Musk Cloud",
    "Amber Coast", "Plum Velvet", "Neroli Sun", "Ginger Wood", "Leather Iris",
    "Pear Blossom", "Cedar Coast", "Rain Moss", "Honey Oud", "Orange Blossom",
]

PRICE_RANGE = {30: (110, 150), 50: (160, 220), 100: (230, 320)}
CASE_SIZE = {30: 6, 50: 6, 100: 4}

# Promotions. True uplift is hidden and only used to generate demand.
# target_sellout_day sets how many gifts the brand supplies (higher = more gifts).
PROMOS = [
    # id, name, type, brand, start, end, discount, gift_item, qualifying_rule, target_sellout_day
    ("PR01", "Valentine's Day GWP", "gwp", "Rosaline", "2025-02-03", "2025-02-16", 0, "Rose travel candle", "Any purchase", 6),
    ("PR02", "Valentine's Day GWP", "gwp", "Nordvik", "2025-02-03", "2025-02-16", 0, "Leather pouch", "Any purchase", 8),
    ("PR03", "Autumn GWP", "gwp", "Atelier Sol", "2025-03-17", "2025-03-30", 0, "10ml travel spray", "50ml or larger", 7),
    ("PR04", "Mother's Day GWP", "gwp", "Lumiere Noire", "2025-04-28", "2025-05-11", 0, "Velvet cosmetic bag", "Any purchase", 5),
    ("PR05", "Mother's Day GWP", "gwp", "Maison Aurel", "2025-04-28", "2025-05-11", 0, "Scented hand cream", "Spend $150 or more", 9),
    ("PR06", "Mid-Year Sale", "discount", "Blanc Studio", "2025-06-20", "2025-06-29", 0.20, "", "", None),
    ("PR07", "Mid-Year Sale", "discount", "Verdant & Co", "2025-06-20", "2025-06-29", 0.20, "", "", None),
    ("PR08", "Father's Day GWP", "gwp", "Nordvik", "2025-08-25", "2025-09-07", 0, "Weekender bag", "Spend $150 or more", 6),
    ("PR09", "Father's Day GWP", "gwp", "Oud Republic", "2025-08-25", "2025-09-07", 0, "Travel case", "Any purchase", 20),
    ("PR10", "Click Frenzy", "discount", "Maison Aurel", "2025-11-11", "2025-11-13", 0.15, "", "", None),
    ("PR11", "Click Frenzy", "discount", "Atelier Sol", "2025-11-11", "2025-11-13", 0.15, "", "", None),
    ("PR12", "Black Friday", "discount", "Lumiere Noire", "2025-11-27", "2025-12-01", 0.20, "", "", None),
    ("PR13", "Black Friday", "discount", "Oud Republic", "2025-11-27", "2025-12-01", 0.20, "", "", None),
    ("PR14", "Black Friday", "discount", "Rosaline", "2025-11-27", "2025-12-01", 0.25, "", "", None),
    ("PR15", "Christmas GWP", "gwp", "Maison Aurel", "2025-12-02", "2025-12-15", 0, "Mini candle set", "Any purchase", 7),
    ("PR16", "Christmas GWP", "gwp", "Verdant & Co", "2025-12-08", "2025-12-21", 0, "Pouch with mini", "50ml or larger", 5),
    ("PR17", "Christmas GWP", "gwp", "Blanc Studio", "2025-12-02", "2025-12-15", 0, "Body lotion 50ml", "Any purchase", 8),
    ("PR18", "Boxing Day Sale", "discount", "Nordvik", "2025-12-26", "2025-12-31", 0.25, "", "", None),
    ("PR19", "Boxing Day Sale", "discount", "Lumiere Noire", "2025-12-26", "2025-12-31", 0.20, "", "", None),
]

GIFT_SUPPLY_FACTOR = 0.6

WEEKDAY_FACTOR = [0.8, 0.8, 0.9, 1.1, 1.1, 1.4, 1.0]  # Mon..Sun

# Shrinkage and claim rates
P_THEFT = {30: 0.004, 50: 0.003, 100: 0.002}
P_DAMAGE = 0.0015
P_TESTER = 0.15          # chance a product opens a new tester on the 1st of the month
P_COUNT_DIFF = 0.03      # chance of a 1-unit count difference at the weekly count (Monday)
P_QUALITY = 0.0004       # quality issue found on a bottle, per product per day
P_RETURN = 0.008         # chance a sold unit is returned
P_RETURN_RESALEABLE = 0.6
P_RECEIPT_DAMAGE = 0.06  # chance a delivery has damaged bottles


def d2s(d):
    return d.isoformat()


def ceil_case(x, case):
    return int(math.ceil(x / case) * case)


def poisson_ppf(u, lam):
    """Inverse Poisson CDF, so the same random number gives the same demand in both runs."""
    if lam <= 0:
        return 0
    k, p = 0, math.exp(-lam)
    c = p
    while u > c and k < 1000:
        k += 1
        p *= lam / k
        c += p
    return k


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def build_products(rng):
    rows = []
    scents = list(SCENTS)
    rng.shuffle(scents)
    i = 0
    for brand, cats in BRANDS:
        for _ in range(5):
            size = int(rng.choice([30, 50, 100], p=[0.25, 0.5, 0.25]))
            lo, hi = PRICE_RANGE[size]
            price = int(round(rng.uniform(lo, hi) / 5) * 5)
            rows.append(dict(
                product_id=f"P{i + 1:03d}", brand=brand,
                product_name=f"{scents[i]} EDP {size}ml",
                category=str(rng.choice(cats)), size_ml=size, price=price,
                cost=round(price * 0.55, 2), case_size=CASE_SIZE[size],
            ))
            i += 1
    df = pd.DataFrame(rows)

    # Popularity tiers: 8 best sellers, 20 mid, 12 slow (weekly units, hidden)
    order = rng.permutation(len(df))
    weekly = np.zeros(len(df))
    weekly[order[:8]] = rng.uniform(8, 14, 8)
    weekly[order[8:28]] = rng.uniform(3, 7, 20)
    weekly[order[28:]] = rng.uniform(0.6, 2.4, 12)
    df["_true_weekly"] = weekly

    df["safety_stock"] = [max(2, math.ceil(w / 7 * C.SAFETY_STOCK_DAYS)) for w in weekly]
    opening = []
    for idx, w in enumerate(weekly):
        o = math.ceil(w * 3)
        if idx in order[28:]:
            o += int(rng.integers(8, 20))  # slow sellers start overstocked
        opening.append(max(2, o))
    df["opening_stock"] = opening
    return df


def season_factor(category, d):
    m = d.month
    f = {1: 0.8, 2: 0.95, 3: 0.95, 4: 0.95, 10: 1.05, 11: 1.15}.get(m, 1.0)
    if date(2025, 2, 1) <= d <= date(2025, 2, 14):
        f *= {"Women": 1.5, "Men": 1.35, "Unisex": 1.3}[category]
    if date(2025, 4, 27) <= d <= date(2025, 5, 11):
        f *= {"Women": 1.8, "Men": 1.0, "Unisex": 1.3}[category]
    if date(2025, 8, 24) <= d <= date(2025, 9, 7):
        f *= {"Women": 1.0, "Men": 1.8, "Unisex": 1.3}[category]
    if date(2025, 11, 24) <= d <= date(2025, 12, 1):
        f *= 1.25  # Black Friday week
    if date(2025, 12, 1) <= d <= date(2025, 12, 24):
        f *= 1.4 + (d.day - 1) / 23 * 1.2  # Christmas ramp
    if date(2025, 12, 26) <= d <= date(2025, 12, 31):
        f *= 1.4
    return f


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

class Sim:
    def __init__(self, rule):
        self.rule = rule
        self.seed = C.RANDOM_SEED
        rng = np.random.default_rng(self.seed)

        self.start = date.fromisoformat(C.START_DATE)
        self.end = date.fromisoformat(C.END_DATE)
        self.days = [self.start + timedelta(i) for i in range((self.end - self.start).days + 1)]
        self.n_days = len(self.days)
        self.closed = {self.idx(date.fromisoformat(s)) for s in C.CLOSED_DAYS}

        self.products = build_products(rng)
        self.P = len(self.products)
        self.prod = self.products.to_dict("records")

        first = self.idx(date.fromisoformat(C.FIRST_ORDER_DATE))
        self.order_days = list(range(first, self.n_days, C.ORDER_INTERVAL_DAYS))

        self._build_promos(rng)

        # History (what the counter can see)
        self.sales = np.zeros((self.P, self.n_days), dtype=int)
        self.close = np.zeros((self.P, self.n_days), dtype=int)
        self.demand = np.zeros((self.P, self.n_days), dtype=int)
        self.price_paid = np.zeros((self.P, self.n_days))

        self.stock = np.array([p["opening_stock"] for p in self.prod], dtype=int)
        self.orders = []          # dicts: p, order_day, arrival, qty, kind
        self.returns_due = {}     # day -> list of (p, qty, impact, value)
        self.sales_rows, self.adj_rows, self.claim_rows = [], [], []
        self.sale_id = self.adj_id = self.claim_id = 0
        self._baseline_cache, self._promo_result_cache = {}, {}

    def idx(self, d):
        return (d - self.start).days

    # -- promotions -----------------------------------------------------------
    def _build_promos(self, rng):
        self.promos = []
        self.promo_by_pday = {}  # (p, day) -> promo index
        for (pid, name, ptype, brand, s, e, disc, gift, rule, target) in PROMOS:
            si, ei = self.idx(date.fromisoformat(s)), self.idx(date.fromisoformat(e))
            members = [i for i, p in enumerate(self.prod) if p["brand"] == brand]
            promo = dict(promo_id=pid, name=name, promo_type=ptype, brand=brand,
                         start=si, end=ei, discount_pct=disc, gift_item=gift,
                         qualifying_rule=rule, members=members, sellout=None, given=0)
            if ptype == "discount":
                promo["_uplift"] = (1 + 3.5 * disc) * rng.uniform(0.9, 1.1)
                promo["gift_qty"] = None
            else:
                promo["_before"] = rng.uniform(3.5, 5.0)
                promo["_after"] = rng.uniform(1.2, 1.6)
                # Brand supplies gifts for about `target` days of qualifying sales.
                # GIFT_SUPPLY_FACTOR < 1 because the brand plans on what the counter usually sells,
                # which is lower than full demand when stock runs short.
                d0 = self.days[si]
                per_day = 0.0
                for m in members:
                    pm = self.prod[m]
                    qualifies = (rule == "Any purchase"
                                 or (rule == "50ml or larger" and pm["size_ml"] >= 50)
                                 or (rule == "Spend $150 or more" and pm["price"] >= 150))
                    if qualifies:
                        per_day += pm["_true_weekly"] / 7 * season_factor(pm["category"], d0)
                per_day *= promo["_before"] * 0.95
                promo["gift_qty"] = max(20, int(round(per_day * target * GIFT_SUPPLY_FACTOR / 10.0)) * 10)
            for m in members:
                for d in range(si, ei + 1):
                    assert (m, d) not in self.promo_by_pday, f"{pid} overlaps another promotion"
                    self.promo_by_pday[(m, d)] = len(self.promos)
            self.promos.append(promo)

    def promo_on(self, p, d):
        k = self.promo_by_pday.get((p, d))
        return None if k is None else self.promos[k]

    def true_uplift(self, p, d, gifts_left_start):
        pr = self.promo_on(p, d)
        if pr is not None:
            if pr["promo_type"] == "discount":
                return pr["_uplift"]
            return pr["_before"] if gifts_left_start[pr["promo_id"]] > 0 else pr["_after"]
        # small dip after a promotion (customers bought early)
        for back in range(1, 15):
            q = self.promo_on(p, d - back)
            if q is not None:
                return 0.85 if q["promo_type"] == "discount" else 0.9
        return 1.0

    # -- run ------------------------------------------------------------------
    def run(self):
        for d in range(self.n_days):
            if d in self.order_days:
                self.place_regular_orders(d)
            self.receive(d)
            self.apply_returns(d)

            gifts_left_start = {}
            for pr in self.promos:
                if pr["promo_type"] == "gwp" and pr["start"] <= d <= pr["end"]:
                    left = pr["gift_qty"] - pr["given"]
                    gifts_left_start[pr["promo_id"]] = left
                    if left <= 0 and pr["sellout"] is None:
                        pr["sellout"] = d

            for p in range(self.P):
                self.simulate_product_day(p, d, gifts_left_start)
            self.close[:, d] = self.stock
            self.check_urgent(d)
        return self

    def simulate_product_day(self, p, d, gifts_left_start):
        prod = self.prod[p]
        day = self.days[d]
        cell = np.random.default_rng([self.seed, p, d])
        u = cell.random(6)  # fixed draw order: demand, theft, damage, tester, count, quality
        pr = self.promo_on(p, d)
        disc = pr["discount_pct"] if pr is not None else 0.0
        unit_price = round(prod["price"] * (1 - disc), 2)
        self.price_paid[p, d] = unit_price

        if d in self.closed:
            return

        # quality issue found on the shelf
        if u[5] < P_QUALITY and self.stock[p] > 0:
            self.stock[p] -= 1
            self.add_claim(d, p, 1, "quality_issue", "decrease", prod["cost"])

        # shrinkage (never more than stock on hand)
        losses = []
        if u[1] < P_THEFT[prod["size_ml"]]:
            losses.append("theft")
        if u[2] < P_DAMAGE:
            losses.append("damage")
        if day.day == 1 and u[3] < P_TESTER:
            losses.append("tester")
        if day.weekday() == 0 and u[4] < P_COUNT_DIFF:
            losses.append("count_difference")
        for reason in losses:
            if self.stock[p] > 0:
                self.stock[p] -= 1
                self.adj_id += 1
                self.adj_rows.append(dict(adj_id=f"A{self.adj_id:05d}", date=d2s(day),
                                          product_id=prod["product_id"], quantity=1, reason=reason))

        # demand and sales
        lam = (prod["_true_weekly"] / 7 * season_factor(prod["category"], day)
               * WEEKDAY_FACTOR[day.weekday()] * self.true_uplift(p, d, gifts_left_start))
        demand = poisson_ppf(u[0], lam)
        sold = min(demand, int(self.stock[p]))
        self.demand[p, d] = demand
        self.sales[p, d] = sold
        self.stock[p] -= sold

        # split into transactions (mostly one bottle each)
        remaining = sold
        while remaining > 0:
            qty = 2 if (remaining >= 2 and cell.random() < 0.08) else 1
            remaining -= qty
            gift = 0
            if pr is not None and pr["promo_type"] == "gwp" and pr["given"] < pr["gift_qty"]:
                rule = pr["qualifying_rule"]
                ok = (rule == "Any purchase"
                      or (rule == "50ml or larger" and prod["size_ml"] >= 50)
                      or (rule == "Spend $150 or more" and qty * unit_price >= 150))
                if ok and cell.random() < 0.95:
                    gift = 1
                    pr["given"] += 1
            self.sale_id += 1
            self.sales_rows.append(dict(
                sale_id=f"S{self.sale_id:06d}", date=d2s(day), product_id=prod["product_id"],
                quantity=qty, unit_price=unit_price, discount_pct=disc,
                promo_id=pr["promo_id"] if pr is not None else "", gift_given=gift))

        # some units come back later as customer returns
        n_ret = int(cell.binomial(sold, P_RETURN)) if sold else 0
        for _ in range(n_ret):
            due = d + int(cell.integers(1, 15))
            if due < self.n_days:
                impact = "increase" if cell.random() < P_RETURN_RESALEABLE else "none"
                self.returns_due.setdefault(due, []).append((p, impact, unit_price))

    def receive(self, d):
        for o in self.orders:
            if o["arrival"] == d:
                p = o["p"]
                self.stock[p] += o["qty"]
                o["received"] = d
                r = np.random.default_rng([self.seed, 99, p, o["order_day"], 1 if o["kind"] == "urgent" else 0])
                if r.random() < P_RECEIPT_DAMAGE:
                    k = min(o["qty"], 2 if r.random() < 0.2 else 1)
                    self.stock[p] -= k
                    self.add_claim(d, p, k, "damaged_on_arrival", "decrease", self.prod[p]["cost"])

    def apply_returns(self, d):
        for p, impact, value in self.returns_due.get(d, []):
            if impact == "increase":
                self.stock[p] += 1
            self.add_claim(d, p, 1, "customer_return", impact, value)

    def add_claim(self, d, p, qty, ctype, impact, unit_value):
        self.claim_id += 1
        r = np.random.default_rng([self.seed, 77, self.claim_id])
        days = {"damaged_on_arrival": (5, 25), "quality_issue": (10, 45), "customer_return": (1, 10)}[ctype]
        lag = int(r.integers(*days)) if r.random() > 0.15 else int(r.integers(40, 76))
        if d + lag > self.n_days - 1:
            status, resolved = "pending", ""
        else:
            x = r.random()
            status = "refunded" if x < 0.75 else ("approved" if x < 0.9 else "rejected")
            resolved = d2s(self.days[d + lag])
        self.claim_rows.append(dict(
            claim_id=f"C{self.claim_id:04d}", submit_date=d2s(self.days[d]),
            product_id=self.prod[p]["product_id"], quantity=qty,
            claim_value=round(qty * unit_value, 2), claim_type=ctype, stock_impact=impact,
            status=status, resolved_date=resolved))

    # -- ordering -------------------------------------------------------------
    def on_order(self, p, d):
        return sum(o["qty"] for o in self.orders if o["p"] == p and o["arrival"] >= d)

    def stock_before(self, p, d):
        return int(self.close[p, d - 1]) if d > 0 else int(self.prod[p]["opening_stock"])

    def next_order_day(self, d):
        later = [x for x in self.order_days if x > d]
        return later[0] if later else d + C.ORDER_INTERVAL_DAYS

    def recent_rate(self, p, d, n):
        """Average daily sales over the last n open days (scaled if fewer are available)."""
        days = [x for x in range(max(0, d - n), d) if x not in self.closed]
        return self.sales[p, days].sum() / len(days) if days else 0.0

    def place(self, p, d, qty, kind):
        if qty > 0:
            self.orders.append(dict(p=p, order_day=d, arrival=d + C.LEAD_TIME_DAYS, qty=int(qty), kind=kind))

    def place_regular_orders(self, d):
        for p in range(self.P):
            case = self.prod[p]["case_size"]
            stock, onord = self.stock_before(p, d), self.on_order(p, d)
            if self.rule == "as_is":
                need = math.ceil(self.recent_rate(p, d, 14) * 14 * (1 + C.AS_IS_BUFFER)) - stock - onord
            else:
                end = d + C.COVERAGE_DAYS
                need = self.forecast(p, d, end) + self.prod[p]["safety_stock"] - stock - onord
            self.place(p, d, ceil_case(need, case) if need > 0 else 0, "regular")

    def check_urgent(self, d):
        nxt = self.next_order_day(d)
        if nxt - d <= C.URGENT_MIN_DAYS_TO_NEXT_ORDER:
            return
        for p in range(self.P):
            if self.stock[p] > self.prod[p]["safety_stock"] or self.on_order(p, d + 1) > 0:
                continue
            case = self.prod[p]["case_size"]
            if self.rule == "as_is":
                need = math.ceil(self.recent_rate(p, d + 1, 7) * 14) - int(self.stock[p])
            else:
                need = (self.forecast(p, d + 1, nxt + C.LEAD_TIME_DAYS)
                        + self.prod[p]["safety_stock"] - int(self.stock[p]))
            self.place(p, d, ceil_case(max(need, 1), case), "urgent")

    # -- to-be rule: baseline, uplift, forecast -------------------------------
    def week_is_clean(self, p, ws, we):
        for x in range(ws, we + 1):
            if self.promo_on(p, x) is not None:
                return False
            if x not in self.closed and self.close[p, x] == 0:
                return False
        return True

    def own_baseline(self, p, t):
        """Weekly baseline from full Mon-Sun weeks before day t, or None."""
        key = (p, t)
        if key in self._baseline_cache:
            return self._baseline_cache[key]
        last_sun = t - 1
        while last_sun >= 0 and self.days[last_sun].weekday() != 6:
            last_sun -= 1
        good = []
        result = None
        for k in range(C.BASELINE_MAX_WEEKS):
            we = last_sun - 7 * k
            ws = we - 6
            if ws < 0:
                break
            if self.week_is_clean(p, ws, we):
                good.append(self.sales[p, ws:we + 1].sum())
            if k + 1 == C.BASELINE_WEEKS and len(good) >= C.BASELINE_MIN_WEEKS:
                break
        if len(good) >= C.BASELINE_MIN_WEEKS:
            result = float(np.mean(good))
        self._baseline_cache[key] = result
        return result

    def baseline(self, p, t):
        b = self.own_baseline(p, t)
        if b is not None:
            return b
        prod = self.prod[p]
        peers = [self.own_baseline(q, t) for q in range(self.P)
                 if q != p and self.prod[q]["brand"] == prod["brand"]
                 and self.prod[q]["category"] == prod["category"]]
        peers = [x for x in peers if x is not None]
        if peers:
            return float(np.mean(peers))
        # cold start: any clean days so far
        days = [x for x in range(max(0, t - 56), t)
                if x not in self.closed and self.promo_on(p, x) is None and self.close[p, x] > 0]
        if len(days) >= 3:
            return float(self.sales[p, days].sum() / len(days) * 7)
        return prod["opening_stock"] / 3  # opening stock was about 3 weeks of cover

    def promo_result(self, pr):
        """Observed uplift for a finished promotion."""
        key = pr["promo_id"]
        if key in self._promo_result_cache:
            return self._promo_result_cache[key]
        before_s = before_b = after_s = after_b = 0.0
        sold_before = 0
        for p in pr["members"]:
            base = self.baseline(p, pr["start"]) / 7
            if base <= 0:
                continue
            for d in range(pr["start"], pr["end"] + 1):
                if d in self.closed:
                    continue
                if self.close[p, d] == 0:
                    continue  # stockout day: sales were capped, skip it
                in_before = pr["promo_type"] == "discount" or pr["sellout"] is None or d < pr["sellout"]
                if in_before:
                    before_s += self.sales[p, d]
                    before_b += base
                    sold_before += self.sales[p, d]
                else:
                    after_s += self.sales[p, d]
                    after_b += base
        res = dict(
            before=before_s / before_b if before_b else None,
            after=after_s / after_b if after_b else None,
            take=(pr["given"] / sold_before) if (pr["promo_type"] == "gwp" and sold_before) else None,
        )
        self._promo_result_cache[key] = res
        return res

    def uplift_estimates(self, t):
        done = [pr for pr in self.promos if pr["end"] < t]
        disc = [self.promo_result(pr)["before"] for pr in done if pr["promo_type"] == "discount"]
        gwp = [self.promo_result(pr) for pr in done if pr["promo_type"] == "gwp"]
        mean = lambda xs, dflt: float(np.mean([x for x in xs if x is not None])) if any(x is not None for x in xs) else dflt
        return dict(
            discount=mean(disc, C.DEFAULT_UPLIFT["discount"]),
            gwp_before=mean([g["before"] for g in gwp], C.DEFAULT_UPLIFT["gwp_before"]),
            gwp_after=mean([g["after"] for g in gwp], C.DEFAULT_UPLIFT["gwp_after"]),
            take=mean([g["take"] for g in gwp], C.DEFAULT_GIFT_TAKE_RATE),
        )

    def forecast(self, p, t, end):
        """Sum of daily baseline x daily uplift from day t up to (not including) end."""
        est = self.uplift_estimates(t)
        base = self.baseline(p, t) / 7
        total = 0.0
        sellout_est = {}
        for d in range(t, end):
            if d in self.closed:
                continue
            pr = self.promo_on(p, d) if d < self.n_days else None
            if pr is None:
                total += base
            elif pr["promo_type"] == "discount":
                total += base * est["discount"]
            else:
                if pr["promo_id"] not in sellout_est:
                    sellout_est[pr["promo_id"]] = self.estimate_sellout(pr, t, est)
                w = min(max(sellout_est[pr["promo_id"]] - d, 0.0), 1.0)
                total += base * (w * est["gwp_before"] + (1 - w) * est["gwp_after"])
        return total

    def estimate_sellout(self, pr, t, est):
        """Estimated (fractional) day index when the gifts run out, by promo_id."""
        if pr["sellout"] is not None and pr["sellout"] <= t:
            return float(pr["sellout"])
        remaining = pr["gift_qty"] - pr["given"]
        start = max(pr["start"], t)
        per_day = sum(self.baseline(q, t) / 7 for q in pr["members"]) * est["gwp_before"] * est["take"]
        if per_day <= 0:
            return float(pr["end"] + 1)
        return start + remaining / per_day

    # -- outputs --------------------------------------------------------------
    def tables(self):
        products = self.products.drop(columns=["_true_weekly"])[
            ["product_id", "brand", "product_name", "category", "size_ml", "price", "cost",
             "safety_stock", "opening_stock", "case_size"]]
        receipts = []
        for i, o in enumerate(sorted(self.orders, key=lambda o: (o["order_day"], o["p"]))):
            got = o["arrival"] < self.n_days
            receipts.append(dict(
                receipt_id=f"R{i + 1:05d}", order_date=d2s(self.days[o["order_day"]]),
                received_date=d2s(self.days[o["arrival"]]) if got else "",
                product_id=self.prod[o["p"]]["product_id"], order_type=o["kind"],
                quantity_ordered=o["qty"], quantity_received=o["qty"] if got else ""))
        promotions = pd.DataFrame([dict(
            promo_id=pr["promo_id"], name=pr["name"], promo_type=pr["promo_type"],
            start_date=d2s(self.days[pr["start"]]), end_date=d2s(self.days[pr["end"]]),
            discount_pct=pr["discount_pct"], brand=pr["brand"], gift_item=pr["gift_item"],
            gift_qty=pr["gift_qty"] if pr["gift_qty"] else "", qualifying_rule=pr["qualifying_rule"])
            for pr in self.promos])
        true_demand = pd.DataFrame([dict(date=d2s(self.days[d]), product_id=self.prod[p]["product_id"],
                                         true_demand=int(self.demand[p, d]))
                                    for d in range(self.n_days) for p in range(self.P)])
        return dict(
            products=products, sales=pd.DataFrame(self.sales_rows),
            stock_receipts=pd.DataFrame(receipts), promotions=promotions,
            stock_adjustments=pd.DataFrame(self.adj_rows), claims=pd.DataFrame(self.claim_rows),
            true_demand=true_demand)

    def metrics(self):
        open_days = [d for d in range(self.n_days) if d not in self.closed]
        cost = self.products["cost"].to_numpy()
        lost_units = self.demand - self.sales
        overstock = 0
        overstock_value = 0.0
        for pr in self.promos:
            for p in pr["members"]:
                e = pr["end"]
                future = self.demand[p, e + 1:e + 29].sum()
                over = max(0, int(self.close[p, e]) - int(future))
                overstock += over
                overstock_value += over * cost[p]
        promo_days = [(p, d) for (p, d) in self.promo_by_pday if d not in self.closed]
        return dict(
            rule=self.rule,
            stockout_days=int(sum((self.close[:, d] == 0).sum() for d in open_days)),
            stockout_days_in_promotions=int(sum(self.close[p, d] == 0 for p, d in promo_days)),
            units_sold=int(self.sales.sum()),
            sales_value=round(float((self.sales * self.price_paid).sum()), 2),
            lost_units=int(lost_units.sum()),
            lost_sales_value=round(float((lost_units * self.price_paid).sum()), 2),
            avg_stock_units=round(float(self.close[:, open_days].sum(axis=0).mean()), 1),
            avg_stock_value_at_cost=round(float((self.close[:, open_days] * cost[:, None]).sum(axis=0).mean()), 2),
            overstock_after_promotions_units=int(overstock),
            overstock_after_promotions_value=round(overstock_value, 2),
            regular_orders=sum(1 for o in self.orders if o["kind"] == "regular"),
            urgent_orders=sum(1 for o in self.orders if o["kind"] == "urgent"),
            units_ordered=sum(o["qty"] for o in self.orders),
        )


def make_messy(sales, seed):
    """A few realistic data quality issues for the Power Query cleaning step."""
    r = np.random.default_rng([seed, 2024])
    s = sales.copy()
    s["discount_pct"] = s["discount_pct"].astype(object)
    n = len(s)
    zero = s.index[s["discount_pct"] == 0]
    blank = r.choice(zero, size=int(len(zero) * 0.02), replace=False)
    s.loc[blank, "discount_pct"] = ""
    fmt = r.choice(n, size=int(n * 0.01), replace=False)
    s.loc[s.index[fmt], "product_id"] = [
        (" " + x) if i % 2 else x.lower() for i, x in enumerate(s.loc[s.index[fmt], "product_id"])]
    dup = s.iloc[r.choice(n, size=int(n * 0.003), replace=False)]
    s = pd.concat([s, dup]).sort_values(["date", "sale_id"], kind="stable").reset_index(drop=True)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule", choices=["as_is", "to_be"], default=C.REORDER_RULE)
    ap.add_argument("--out", default="data", help="output folder (raw/ and validation/ go inside)")
    ap.add_argument("--clean", action="store_true", help="do not add data quality issues")
    args = ap.parse_args()

    sim = Sim(args.rule).run()
    t = sim.tables()
    out = Path(args.out) if Path(args.out).is_absolute() else ROOT / args.out
    (out / "raw").mkdir(parents=True, exist_ok=True)
    (out / "validation").mkdir(parents=True, exist_ok=True)

    sales = t["sales"]
    if C.MESSY_RAW_DATA and not args.clean:
        sales = make_messy(sales, C.RANDOM_SEED)
    for name in ["products", "stock_receipts", "promotions", "stock_adjustments", "claims"]:
        t[name].to_csv(out / "raw" / f"{name}.csv", index=False)
    sales.to_csv(out / "raw" / "sales.csv", index=False)
    t["true_demand"].to_csv(out / "validation" / "true_demand.csv", index=False)

    m = sim.metrics()
    (out / "validation" / f"metrics_{args.rule}.json").write_text(json.dumps(m, indent=2))
    print(json.dumps(m, indent=2))


if __name__ == "__main__":
    main()
