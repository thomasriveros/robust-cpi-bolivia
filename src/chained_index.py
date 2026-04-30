"""
src/chained_index.py
====================
Monthly-Chained Daily Jevons CPI Engine
----------------------------------------

Methodology  (R-equivalent hybrid approach)
-----------
Price relatives are computed as:

    relative(d, M) = P_d  /  avg_price(M-1)

where avg_price(M-1) is the MEAN price of each product over the PREVIOUS calendar
month.  Using a monthly average (rather than a single reference day) suppresses
link-day noise and avoids the "first-day of month" outlier problem.

Chain formula:
    I_total(d) = 100  ×  relative(d, M)  ×  running_multiplier

    running_multiplier  =  PRODUCT of [ relative(last_day, M-1) for all past months ]

At each month boundary the last day's weighted national relative becomes the new
chain link multiplier.  This exactly replicates the R cumprod trick:
    chain_multiplier[first_day_of_M] = relative(last_day_of_M-1)
    running_multiplier = cumprod(chain_multipliers)

References
----------
See scripts/chained_tracker_supermarket_*.py for usage.
"""

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Core 5 categories and their official INE weights (decimal)
# ---------------------------------------------------------------------------
CHAINED_CORE_CATEGORIES = [
    "Alimentos y Bebidas No Alcohólicas",
    "Bienes y Servicios Diversos",
    "Muebles, Bienes y Servicios Domésticos",
    "Bebidas Alcohólicas y Tabaco",
    "Prendas de Vestir y Calzado",
]

# Raw INE weights for the Core 5 (will be re-normalized to sum to 1.0)
_RAW_WEIGHTS = {
    "Alimentos y Bebidas No Alcohólicas": 27.06,
    "Bienes y Servicios Diversos":         7.55,
    "Muebles, Bienes y Servicios Domésticos": 6.08,
    "Bebidas Alcohólicas y Tabaco":         0.88,
    "Prendas de Vestir y Calzado":          7.56,
}

_TOTAL_RAW = sum(_RAW_WEIGHTS.values())
CHAINED_WEIGHTS = {cat: w / _TOTAL_RAW for cat, w in _RAW_WEIGHTS.items()}


# ---------------------------------------------------------------------------
# Outlier bounds — kept as reference constants but NOT applied by default.
# ---------------------------------------------------------------------------
# In a day-on-day chain, symmetric bounds prevent chain drift:
#   if a -60% drop is excluded, the recovery +60% must also be excluded.
# In the MONTHLY-CHAINED approach, relatives (P_d / P_month_start) are
# computed fresh each day — there is no compounding, so asymmetric filtering
# does NOT accumulate.  Applying strict caps here causes a systematic
# downward bias by dropping genuine large price increases.
# The constants below are kept for reference; pass them explicitly to
# calculate_direct_relative() only if you want to enable filtering.
LOWER_BOUND = 0.45
UPPER_BOUND = 1.0 / LOWER_BOUND   # ≈ 2.2222


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def build_month_snapshot(df, id_col="mapped_id", price_col="price",
                          category_col="Category", min_n=10):
    """
    Build a month-start basket snapshot from a DataFrame of daily observations.

    The snapshot is a per-product reference price used as the denominator in all
    within-month Jevons relatives.  Only products belonging to the Core 5
    categories are included.  Categories with fewer than ``min_n`` products are
    excluded so that thin categories cannot anchor the basket.

    Parameters
    ----------
    df : pd.DataFrame
        Today's (month-start day) data with at least ``id_col``, ``price_col``,
        ``category_col`` columns.
    id_col : str
        Column containing the normalised product ID.
    price_col : str
        Column containing the numeric price.
    category_col : str
        Column containing the INE category string.
    min_n : int
        Minimum number of products required to include a category in the snapshot.

    Returns
    -------
    snapshot : pd.DataFrame
        DataFrame indexed by ``id_col`` with columns [``price_col``, ``category_col``].
        Only Core 5 categories with ≥ min_n products are retained.
    valid_categories : list[str]
        Categories that passed the min_n filter and are part of the new basket.
    """
    df = df.copy()

    # Keep Core 5 only
    df = df[df[category_col].isin(CHAINED_CORE_CATEGORIES)].copy()

    # Ensure numeric prices
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
    df = df.dropna(subset=[id_col, price_col, category_col])
    df = df[df[price_col] > 0]

    # Drop duplicate product IDs within the same day — take first occurrence
    df = df.drop_duplicates(subset=[id_col])

    # Count products per category BEFORE filtering
    cat_counts = df.groupby(category_col)[id_col].count()
    valid_cats = cat_counts[cat_counts >= min_n].index.tolist()

    snapshot = df[df[category_col].isin(valid_cats)][[id_col, price_col, category_col]].set_index(id_col)

    return snapshot, valid_cats


def build_link_prices(month_data, id_col="mapped_id", price_col="price",
                      category_col="Category", min_n=10):
    """
    Compute the **mean price per product** across all observations in a month.

    This is used as the reference denominator for the FOLLOWING month's daily
    Jevons relatives, replicating the R ``monthly_bases`` step:

        relative(d, M) = P_d / avg_price(M-1)

    Using a monthly average rather than a single reference day suppresses
    link-day volatility (restocking, end-of-month promotions, etc.).

    Parameters
    ----------
    month_data : pd.DataFrame
        All observations from the previous calendar month.
    id_col, price_col, category_col : str
        Column names.
    min_n : int
        Minimum distinct products per category to keep it in the link basket.

    Returns
    -------
    link_df : pd.DataFrame or None
        DataFrame indexed by ``id_col`` with columns [``price_col``, ``category_col``].
        ``price_col`` contains the mean price over the month.
        Returns ``None`` if no valid data.
    valid_cats : list[str]
    """
    df = month_data.copy()
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
    df = df.dropna(subset=[id_col, price_col, category_col])
    df = df[df[price_col] > 0]
    df = df[df[category_col].isin(CHAINED_CORE_CATEGORIES)]

    if df.empty:
        return None, []

    # Mean price per product over the entire month
    avg = (df.groupby([id_col, category_col])[price_col]
             .mean()
             .reset_index())

    # Category min-N filter
    counts = avg.groupby(category_col)[id_col].count()
    valid_cats = counts[counts >= min_n].index.tolist()
    avg = avg[avg[category_col].isin(valid_cats)]

    if avg.empty:
        return None, []

    link_df = avg.set_index(id_col)
    return link_df, valid_cats


def calculate_direct_relative(current_df, snapshot, id_col="mapped_id",
                               price_col="price", category_col="Category",
                               min_n=10, lower_bound=None, upper_bound=None):
    """
    Compute category-level Jevons price relatives: P_today / P_month_start.

    Only products present in BOTH ``current_df`` and the ``snapshot`` are used
    (matched-model inner join).  Categories with fewer than ``min_n`` matched
    products are excluded.

    Parameters
    ----------
    current_df : pd.DataFrame
        Today's data with ``id_col``, ``price_col``, ``category_col``.
    snapshot : pd.DataFrame
        The month-start snapshot returned by :func:`build_month_snapshot`,
        indexed by ``id_col``.
    id_col, price_col, category_col : str
        Column names (must match those used when building the snapshot).
    min_n : int
        Minimum matched products required per category.
    lower_bound : float or None
        Lower outlier cut-off for P_d/P_start relatives.  ``None`` = no filter.
        In a monthly-chained index this is typically left as ``None`` because
        relatives are recomputed fresh each day (no chain-drift accumulation).
    upper_bound : float or None
        Upper outlier cut-off.  ``None`` = no filter.

    Returns
    -------
    pd.Series
        Jevons relative per category (e.g., 1.002 means +0.2 % vs month-start).
        Categories that fail the min_n filter are absent from the Series.
    """
    if snapshot is None or snapshot.empty:
        return pd.Series(dtype=float)

    current = current_df.copy()
    current[price_col] = pd.to_numeric(current[price_col], errors="coerce")
    current = current.dropna(subset=[id_col, price_col, category_col])
    current = current[current[price_col] > 0]

    # Keep Core 5 and snapshot categories only
    basket_cats = snapshot[category_col].unique().tolist()
    current = current[current[category_col].isin(basket_cats)]

    # Inner join: products present today AND in the month-start snapshot
    merged = current[[id_col, price_col, category_col]].merge(
        snapshot[[price_col]].rename(columns={price_col: "price_start"}),
        left_on=id_col,
        right_index=True,
        how="inner",
    )

    if merged.empty:
        return pd.Series(dtype=float)

    merged["relative"] = merged[price_col] / merged["price_start"]

    # Optional outlier filter — disabled by default for monthly-chained indexes
    if lower_bound is not None:
        merged = merged[merged["relative"] >= lower_bound]
    if upper_bound is not None:
        merged = merged[merged["relative"] <= upper_bound]

    # Min-N filter per category
    cat_counts = merged.groupby(category_col).size()
    valid_cats = cat_counts[cat_counts >= min_n].index
    merged = merged[merged[category_col].isin(valid_cats)]

    if merged.empty:
        return pd.Series(dtype=float)

    # Jevons geometric mean per category
    def geo_mean(x):
        return np.exp(np.log(x).mean())

    return merged.groupby(category_col)["relative"].agg(geo_mean)


def compute_today_indices(month_anchors, within_month_relatives):
    """
    Compute today's chain-level sub-indices as: anchor × within-month relative.

    The key insight: ``within_month_relatives`` from :func:`calculate_direct_relative`
    are already **levels** relative to the month-start (P_today / P_month_start),
    NOT day-on-day changes.  Therefore we must NOT multiply them cumulatively
    each day — we multiply the *frozen monthly anchor* by today's level.

    Formula::

        I_total(d) = anchor[cat]  ×  Jevons(P_d / P_month_start)

    Categories absent from ``within_month_relatives`` (insufficient matched
    products) carry forward the anchor value unchanged (imputation = no change).

    Parameters
    ----------
    month_anchors : dict
        Frozen chain-level values at the END of the previous month,
        e.g. ``{"Alimentos...": 127.3, ...}``.
        These are **not mutated** during the month — only updated at chain-link.
    within_month_relatives : pd.Series
        Output of :func:`calculate_direct_relative`.
        Each value is P_today / P_month_start (≈ 1.00 on day 1).

    Returns
    -------
    today_indices : dict
        Today's index levels (anchor × relative for each category).
    """
    today = month_anchors.copy()
    for cat, relative in within_month_relatives.items():
        if cat in today:
            today[cat] = month_anchors[cat] * relative
        else:
            # Brand-new category — initialise anchor at 100 and apply relative
            today[cat] = 100.0 * relative
    return today


def compute_total_cpi(today_indices, available_categories=None):
    """
    Compute the weighted aggregate CPI from today's chain-level sub-indices.

    Weights are drawn from :data:`CHAINED_WEIGHTS` and re-normalised across
    whichever ``available_categories`` are present in ``today_indices``.

    Parameters
    ----------
    today_indices : dict
        Today's index levels (output of :func:`compute_today_indices` or
        the month anchors on forward-fill days).
    available_categories : list[str] or None
        If provided, only these categories participate in the weighted average.
        Defaults to all keys in ``today_indices``.

    Returns
    -------
    float
        The weighted CPI level.
    """
    if available_categories is None:
        available_categories = list(today_indices.keys())

    active = [c for c in available_categories
              if c in today_indices and c in CHAINED_WEIGHTS]

    if not active:
        return 100.0

    raw_weights = {c: CHAINED_WEIGHTS[c] for c in active}
    total_w = sum(raw_weights.values())
    norm_weights = {c: w / total_w for c, w in raw_weights.items()}

    return sum(today_indices[c] * norm_weights[c] for c in active)


def lock_month_anchor(today_indices, prev_anchors=None):
    """
    Called at month-end (= on the first day of the NEW month, before building
    the new snapshot).  Freezes ``today_indices`` as the new anchor values that
    will be multiplied by within-month relatives for the coming month.

    Any categories not yet in ``today_indices`` inherit their value from
    ``prev_anchors`` (or 100.0 if completely new).

    Parameters
    ----------
    today_indices : dict
        The final computed index levels at the end of the previous month.
    prev_anchors : dict or None
        Previous anchor dict (used to preserve carry-forward values).

    Returns
    -------
    new_anchors : dict
    """
    new_anchors = {} if prev_anchors is None else prev_anchors.copy()
    new_anchors.update(today_indices)   # overwrite with latest values
    return new_anchors


def start_new_month(current_df, month_anchors, id_col="mapped_id",
                    price_col="price", category_col="Category", min_n=10):
    """
    Called on the first day of a new calendar month.

    1. Takes ``month_anchors`` as-is — these are already locked end-of-last-month
       levels and do NOT change today.
    2. Builds a fresh basket snapshot from ``current_df``.
    3. Initialises any brand-new categories at 100.0 in the anchors.

    Parameters
    ----------
    current_df : pd.DataFrame
        Today's full data (first observed day of the new month).
    month_anchors : dict
        Frozen chain-level indices from the end of the previous month.
    id_col, price_col, category_col, min_n :
        Forwarded to :func:`build_month_snapshot`.

    Returns
    -------
    snapshot : pd.DataFrame
        New month-start reference prices.
    active_cats : list[str]
        Categories in the new basket.
    updated_anchors : dict
        Anchors with any new categories initialised at 100.0.
    """
    snapshot, valid_cats = build_month_snapshot(
        current_df, id_col=id_col, price_col=price_col,
        category_col=category_col, min_n=min_n,
    )

    updated_anchors = month_anchors.copy()
    for cat in valid_cats:
        if cat not in updated_anchors:
            updated_anchors[cat] = 100.0

    return snapshot, valid_cats, updated_anchors
