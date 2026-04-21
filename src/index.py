import pandas as pd
import numpy as np

def calculate_daily_change(current_df, previous_df, id_col='id', price_col='price', category_col='Category'):
    """
    Calculates the category-level price relative using the Matched Model approach.
    
    Args:
        current_df: DataFrame of current day's products with 'id', 'price', 'Category'.
        previous_df: DataFrame of previous day's products with 'id', 'price'.
        id_col: Column name for product ID.
        price_col: Column name for price.
        category_col: Column name for category.
        
    Returns:
        pd.Series: A series indexed by 'Category' containing the daily geometric mean of price relatives.
        (e.g., Cat A: 1.002, Cat B: 0.998)
    """
    # Merge current and previous on product ID to find matched models (Inner Join)
    # This ensures we only compare products that exist in BOTH periods.
    merged = pd.merge(
        current_df[[id_col, price_col, category_col]],
        previous_df[[id_col, price_col]],
        on=id_col,
        how='inner',
        suffixes=('_cur', '_prev')
    )
    
    if merged.empty:
        return pd.Series(dtype=float)

    # Calculate individual price relative: P_t / P_{t-1}
    # Ensure prices are numeric
    merged['price_cur'] = pd.to_numeric(merged['price_cur'], errors='coerce')
    merged['price_prev'] = pd.to_numeric(merged['price_prev'], errors='coerce')
    
    # Drop NaNs
    merged = merged.dropna(subset=['price_cur', 'price_prev'])
    
    # Handle zero prices if any (though unlikely for supermarket data)
    merged = merged[(merged['price_cur'] > 0) & (merged['price_prev'] > 0)]
    
    merged['relative'] = merged['price_cur'] / merged['price_prev']
    
    # Apply Outlier Cap
    # Filter out extreme price swings (drops > 50%)
    # Upper bound set to 2.2x to safely permit 50% off sales reverting back to normal pricing
    merged = merged[(merged['relative'] >= 0.5) & (merged['relative'] <= 2.2)]
    
    # Apply Robust Category Filter (N >= 30)
    # Only calculate Jevons index for categories that have at least 30 matched products today.
    # Categories with < 30 will effectively be 'carried forward' with 0% inflation today.
    category_counts = merged.groupby(category_col).size()
    valid_categories = category_counts[category_counts >= 30].index
    merged = merged[merged[category_col].isin(valid_categories)]

    # Calculate geometric mean of relatives per category (Jevons Index)
    # Function for geometric mean: exp(mean(log(x)))
    def geometric_mean(x):
        return np.exp(np.log(x).mean())

    category_changes = merged.groupby(category_col)['relative'].agg(geometric_mean)
    
    return category_changes

def normalize_weights(weights_df, available_categories):
    """
    Re-normalizes weights based on available categories.
    If a category is completely missing from `available_categories`, its weight is distributed
    proportionally to the others.
    
    Args:
        weights_df: DataFrame with 'Category' and 'Weight'.
        available_categories: List-like of categories present in the data.
        
    Returns:
        pd.Series: Normalized weights indexed by Category (summing to 1.0).
    """
    # Filter for weights of categories that are present
    mask = weights_df['Category'].isin(available_categories)
    active_weights = weights_df[mask].set_index('Category')['Weight']
    
    if active_weights.empty:
        return pd.Series(dtype=float)
        
    # Re-normalize
    total_active_weight = active_weights.sum()
    
    # If total weight is effectively zero, return empty (avoid div by zero)
    if total_active_weight == 0:
        return pd.Series(dtype=float)

    normalized_weights = active_weights / total_active_weight
    
    return normalized_weights

def calculate_index(current_sub_indices, category_changes, weights_df, present_categories=None):
    """
    Updates the sub-indices and calculates the aggregate CPI.
    
    Args:
        current_sub_indices: Dict {Category: IndexValue} (e.g., {'Food': 105.2})
                             Base period logic: Initial values should be 100.0 if starting fresh.
        category_changes: Series of daily changes (relatives) for categories.
                          If a category has no matched products, it won't be in here.
        weights_df: DataFrame with official weights.
        present_categories: List-like of categories present in the current data. 
                            Used to initialize new categories that appear for the first time.
        
    Returns:
        tuple: (updated_sub_indices (dict), total_cpi (float), active_categories (list))
    """
    updated_sub_indices = current_sub_indices.copy()
    
    # Update sub-indices for categories that have changed
    for cat, change in category_changes.items():
        if cat in updated_sub_indices:
            updated_sub_indices[cat] *= change
        else:
            # If a category is in changes but not in indices (unexpected if initialized correctly),
            # we initialize it at 100 * change.
            updated_sub_indices[cat] = 100.0 * change

    # Handle NEW categories that appeared today but might not have a change (e.g. if no match yet? 
    # But if they are new, they certainly won't have a match).
    # We purposefully do not initialize categories into the index until they generate a valid 
    # daily matched calculation (change). This prevents sparse categories (like those with only 
    # 1 product present) from being injected at 100.0 and dragging down the total CPI.
    
    # For categories NOT in category_changes (no matched products today),
    # we implicitly carry forward the previous index value (multiply by 1.0).
    # So `updated_sub_indices` already has the correct values for them.
    
    # Identify "Active" categories for structural weight re-normalization
    # The requirement: "If a category ... has zero products ... re-normalize".
    # This implies we check which categories are existent in the index calculation.
    # If we have a sub-index for it, it "exists" historically.
    # But if it has "zero products in the Ketal data", should we exclude it from Total CPI?
    # Yes, per user instruction.
    
    # We need to know which categories are "present" in today's data to decide whether to include them in the weighted sum.
    # This is slightly different from `category_changes` (matched products). One might have products but no matches.
    # However, `category_changes` is the best proxy for "measurable" categories.
    # If we carry forward a price (imputation), we usually keep the weight.
    # Re-normalization is for *missing* data, e.g., Housing is never scraped.
    # So we should probably base re-normalization on the intersection of 
    # `weights_df['Category']` and `category_changes.index`?
    # No, that's too strict. If 'Food' has no matches for one day (unlikely), we shouldn't drop it.
    
    # Let's stick to the list of categories that HAVE a sub-index as the "Active Universe".
    # If a category was NEVER seen, it won't be in `updated_sub_indices`. 
    # Then `normalize_weights` will exclude it, effectively satisfying the requirement 
    # for categories like "Housing" that never appear in Ketal data.
    
    active_categories = list(updated_sub_indices.keys())
    
    normalized_weights = normalize_weights(weights_df, active_categories)
    
    total_cpi = 0.0
    for cat, weight in normalized_weights.items():
        total_cpi += updated_sub_indices[cat] * weight
        
    return updated_sub_indices, total_cpi, active_categories
