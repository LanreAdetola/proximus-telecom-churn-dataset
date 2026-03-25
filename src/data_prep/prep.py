"""
Proximus Churn — Data Preparation
Cleans raw CSV, encodes categoricals, splits into train/test, and writes
parquet outputs for downstream training.
"""

import argparse
import os

import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split


def parse_args():
    parser = argparse.ArgumentParser(description="Prepare Proximus churn data")
    parser.add_argument("--input-data", type=str, required=True, help="Path to raw churn CSV")
    parser.add_argument("--output-train", type=str, required=True, help="Output dir for train split")
    parser.add_argument("--output-test", type=str, required=True, help="Output dir for test split")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-seed", type=int, default=42)
    return parser.parse_args()


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning: drop duplicates, handle nulls, normalise column names."""
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df = df.drop_duplicates()
    # Fill numeric nulls with median, categorical with mode
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna(df[col].mode()[0])
    return df


def encode(df: pd.DataFrame) -> pd.DataFrame:
    """Encode target to binary 0/1 and one-hot encode remaining categoricals."""
    # Target encoding
    df["churn"] = df["churn"].map({"Yes": 1, "No": 0}).astype(int)

    # One-hot encode categorical features
    cat_cols = df.select_dtypes(include="object").columns.tolist()
    df = pd.get_dummies(df, columns=cat_cols, drop_first=True, dtype=int)
    return df


def main():
    args = parse_args()
    mlflow.start_run()

    # --- Load -----------------------------------------------------------------
    df = pd.read_csv(args.input_data)
    mlflow.log_metric("raw_rows", len(df))
    mlflow.log_metric("raw_cols", len(df.columns))

    # --- Clean ----------------------------------------------------------------
    df = clean(df)
    mlflow.log_metric("clean_rows", len(df))

    # --- Encode ---------------------------------------------------------------
    df = encode(df)
    mlflow.log_metric("encoded_features", len(df.columns) - 1)

    # --- Split ----------------------------------------------------------------
    train_df, test_df = train_test_split(
        df, test_size=args.test_size, random_state=args.random_seed, stratify=df["churn"]
    )
    mlflow.log_metric("train_rows", len(train_df))
    mlflow.log_metric("test_rows", len(test_df))

    # --- Write ----------------------------------------------------------------
    os.makedirs(args.output_train, exist_ok=True)
    os.makedirs(args.output_test, exist_ok=True)

    train_df.to_parquet(os.path.join(args.output_train, "train.parquet"), index=False)
    test_df.to_parquet(os.path.join(args.output_test, "test.parquet"), index=False)

    mlflow.end_run()
    print(f"Data prep complete — train: {len(train_df)}, test: {len(test_df)}")


if __name__ == "__main__":
    main()
