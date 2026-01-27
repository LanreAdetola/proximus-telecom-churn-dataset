# 📡 Proximus Telecom Churn Dataset (Belgium)

## Overview

This project provides a **synthetic but realistic telecom customer dataset** based on **publicly available Proximus mobile plan information** and **Belgium-specific demographics**.

The dataset is designed for **learning supervised classification**, with a focus on **customer churn prediction**.

All data is **ethically generated**:

* No web scraping
* No personal or sensitive data
* No proprietary information

The goal is to simulate how a **real telecom churn dataset behaves**, while remaining fully explainable.

---

## Problem Statement

**Can we predict whether a mobile customer will churn based on their usage, billing, network experience, and relationship history?**

* **Task type:** Binary classification
* **Target variable:** `churn` (`Yes` / `No`)
* **Context:** Mobile customers of a single Belgian provider (Proximus)

---

## Dataset Design Philosophy

This dataset was intentionally designed to balance:

* **Realism** – values reflect real telecom behavior
* **Explainability** – every column has a clear meaning
* **Learning value** – includes noise, imbalance, and correlations
* **Reproducibility** – frozen distributions and fixed random seed

Rather than copying real customer data, **business rules and probabilities** are used to simulate customer behavior.

---

## Data Source (Plan-Level)

Mobile plans are derived from **public Proximus mobile subscription information**, including:

* Data allowances
* Monthly pricing
* Network type (4G / 5G)
* Advertised speeds
* Contract flexibility

Promotional pricing is ignored to reflect **long-term customer behavior**.

---

## Dataset Structure

### Size

* **1,000 customers**
* One row per customer

---

## 🧾 Plan Information

| Column                | Description                              |
| --------------------- | ---------------------------------------- |
| `plan_name`           | Proximus mobile plan                     |
| `plan_data_gb`        | Monthly data allowance (999 = unlimited) |
| `plan_price_eur`      | Monthly price (€)                        |
| `plan_max_speed_mbps` | Advertised max download speed            |
| `plan_network_type`   | 4G or 5G                                 |
| `contract_type`       | Month-to-month                           |

---

## 📍 Demographics

| Column   | Description                    |
| -------- | ------------------------------ |
| `age`    | Customer age (18–80)           |
| `city`   | Real Belgian city              |
| `region` | Flanders / Wallonia / Brussels |
| `urban`  | Urban vs non-urban area        |

---

## 📱 Usage Behavior

| Column                 | Description                          |
| ---------------------- | ------------------------------------ |
| `monthly_data_gb`      | Data usage per month                 |
| `monthly_call_minutes` | Total call minutes                   |
| `monthly_sms`          | SMS messages sent                    |
| `international_calls`  | Whether international calls are made |

Usage is **constrained by plan limits**, but includes realistic variability.

---

## 💳 Billing & Relationship

| Column                   | Description                         |
| ------------------------ | ----------------------------------- |
| `payment_method`         | Direct debit / Bank transfer / Card |
| `customer_tenure_months` | Time with provider                  |

Tenure is skewed toward newer customers, reflecting real churn dynamics.

---

## 📡 Network Quality

| Column                             | Description                              |
| ---------------------------------- | ---------------------------------------- |
| `avg_download_speed_mbps`          | Experienced speed (below advertised max) |
| `network_complaints_last_6_months` | Logged complaints                        |
| `dropped_calls_per_month`          | Call reliability indicator               |

---

## 🎯 Target Variable

| Column  | Description                  |
| ------- | ---------------------------- |
| `churn` | Whether the customer churned |

---

## Churn Generation Logic (Important)

Churn is **not assigned by hard rules**.

Instead:

1. A **churn risk score** is computed based on:

   * High price
   * Short tenure
   * Network complaints
   * Under-utilization of plan
2. The score is converted into a **probability** using a sigmoid function
3. Churn is **sampled probabilistically**

This creates:

* Natural class imbalance (~20–30% churn)
* Realistic uncertainty
* No perfect decision boundaries

---

## Why This Dataset Is Useful

This dataset is ideal for practicing:

* Logistic Regression
* Decision Trees
* Random Forests
* Feature importance analysis
* Precision / Recall trade-offs
* Model explainability

It also supports **EDA exercises**, such as:

* Churn vs tenure
* Churn by plan
* Complaints vs churn

---

## Ethical Considerations

* No real customer data
* No personal identifiers
* No protected attributes
* Fully synthetic and explainable

---

## How to Generate the Dataset

Run the generator script:

```bash
python proximus_dataset_generator_v2.py
```

Output:

```text
proximus_customers_1000.csv
```

---

## Potential Extensions

* Add time-based churn (multi-period simulation)
* Introduce customer segments
* Increase dataset size
* Test imbalance-handling techniques
* Compare models before/after noise injection

---

## Intended Use

This dataset is intended for:
- Education and coursework
- Learning supervised classification
- Portfolio and demonstration projects

It is **not** intended to represent real Proximus customers or to be used for commercial decision-making.



## License

This dataset is intended for **educational and learning purposes only**.

