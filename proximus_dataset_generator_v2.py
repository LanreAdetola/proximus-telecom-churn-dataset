
import numpy as np
import pandas as pd

# =====================================================
# Proximus Telecom Dataset Generator (Improved Version)
# - Probabilistic churn
# - Frozen distributions
# - Fully explainable
# =====================================================

# Reproducibility
np.random.seed(42)

# -----------------------------
# Proximus plan table
# -----------------------------
plans = pd.DataFrame({
    "plan_name": [
        "Mobile Essential",
        "Mobile Easy",
        "Mobile Smart",
        "Mobile Maxi",
        "Mobile Unlimited"
    ],
    "plan_data_gb": [5, 10, 60, 120, 999],  # 999 = unlimited
    "plan_price_eur": [16.99, 19.99, 24.99, 29.99, 49.99],
    "plan_max_speed_mbps": [220, 250, 500, 500, 1000],
    "plan_network_type": ["4G", "5G", "5G", "5G", "5G"]
})

# -----------------------------
# Belgian cities mapping
# -----------------------------
cities = {
    "Brussels": ("Brussels", True),
    "Antwerp": ("Flanders", True),
    "Ghent": ("Flanders", True),
    "Leuven": ("Flanders", True),
    "Mechelen": ("Flanders", False),
    "Hasselt": ("Flanders", False),
    "Liège": ("Wallonia", True),
    "Namur": ("Wallonia", False),
    "Charleroi": ("Wallonia", True),
    "Mons": ("Wallonia", False)
}

city_names = list(cities.keys())
city_weights = [0.18, 0.15, 0.10, 0.08, 0.07, 0.07, 0.12, 0.07, 0.10, 0.06]

# -----------------------------
# Sample customers
# -----------------------------
n_customers = 1000
plan_weights = [0.20, 0.25, 0.30, 0.15, 0.10]

customers = plans.sample(
    n=n_customers,
    replace=True,
    weights=plan_weights
).reset_index(drop=True)

# -----------------------------
# Demographics
# -----------------------------
customers["age"] = np.clip(
    np.random.normal(loc=40, scale=12, size=n_customers).astype(int),
    18,
    80
)

customers["city"] = np.random.choice(
    city_names,
    size=n_customers,
    p=city_weights
)

customers["region"] = customers["city"].apply(lambda c: cities[c][0])
customers["urban"] = customers["city"].apply(lambda c: "Yes" if cities[c][1] else "No")

# -----------------------------
# Usage behavior
# -----------------------------
def generate_data_usage(plan_cap):
    if plan_cap == 999:
        return np.round(np.random.uniform(30, 200), 1)
    return np.round(np.random.uniform(0.4 * plan_cap, 1.2 * plan_cap), 1)

customers["monthly_data_gb"] = customers["plan_data_gb"].apply(generate_data_usage)

customers["monthly_call_minutes"] = np.clip(
    np.random.gamma(shape=2.5, scale=200, size=n_customers).astype(int),
    50,
    2000
)

customers["monthly_sms"] = np.clip(
    np.random.exponential(scale=40, size=n_customers).astype(int),
    0,
    500
)

customers["international_calls"] = np.random.choice(
    ["Yes", "No"],
    size=n_customers,
    p=[0.20, 0.80]
)

# -----------------------------
# Billing & relationship
# -----------------------------
customers["payment_method"] = np.random.choice(
    ["Direct debit", "Bank transfer", "Card"],
    size=n_customers,
    p=[0.78, 0.18, 0.04]
)

customers["customer_tenure_months"] = np.clip(
    np.random.exponential(scale=24, size=n_customers).astype(int) + 1,
    1,
    120
)

# -----------------------------
# Network quality
# -----------------------------
def generate_speed(max_speed, urban):
    base = np.random.uniform(0.3, 0.7) * max_speed
    if urban == "Yes":
        base *= np.random.uniform(1.05, 1.15)
    return int(min(base, max_speed))

customers["avg_download_speed_mbps"] = customers.apply(
    lambda row: generate_speed(row["plan_max_speed_mbps"], row["urban"]),
    axis=1
)

customers["network_complaints_last_6_months"] = np.random.choice(
    [0, 1, 2, 3, 4],
    size=n_customers,
    p=[0.60, 0.25, 0.10, 0.04, 0.01]
)

customers["dropped_calls_per_month"] = np.clip(
    np.random.poisson(lam=1.2, size=n_customers),
    0,
    10
)

# -----------------------------
# Churn generation (probabilistic)
# -----------------------------
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

churn_score = (
    (customers["plan_price_eur"] > 30).astype(int) * 1.0 +
    (customers["customer_tenure_months"] < 12).astype(int) * 1.3 +
    (customers["network_complaints_last_6_months"] >= 2).astype(int) * 1.8 +
    (customers["monthly_data_gb"] < 0.3 * customers["plan_data_gb"]).astype(int) * 0.9
)

churn_probability = sigmoid(churn_score - 2.0)

customers["churn"] = np.where(
    np.random.rand(n_customers) < churn_probability,
    "Yes",
    "No"
)

# -----------------------------
# Finalize & export
# -----------------------------
customers["contract_type"] = "Month-to-month"

customers.to_csv("proximus_customers_1000.csv", index=False)

print("Dataset generated: proximus_customers_1000.csv")
