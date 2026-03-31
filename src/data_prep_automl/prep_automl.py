"""
Proximus Churn — Data Preparation for AutoML
Cleans the raw CSV and outputs:
  - An MLTable (train set) for the AutoML step
  - A parquet (test set) for post-AutoML evaluation

Key difference from the standard prep.py:
  AutoML requires MLTable format when used as a pipeline step.
  MLTable = a folder containing an MLTable YAML + the actual data file.
  AutoML handles its own encoding/featurization, so we do NOT one-hot encode here.
"""

import argparse
import os

import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split


def parse_args():
    parser = argparse.ArgumentParser(description="Prepare data for AutoML")
    parser.add_argument("--input-data", type=str, required=True)
    parser.add_argument("--output-train", type=str, required=True)
    parser.add_argument("--output-test", type=str, required=True)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-seed", type=int, default=42)
    return parser.parse_args()


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise column names, drop duplicates, fill missing values."""
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df = df.drop_duplicates()
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna(df[col].mode()[0])
    return df


def write_mltable(df: pd.DataFrame, output_dir: str) -> None:
    """
    Write a DataFrame as an MLTable: a CSV file + an MLTable YAML spec.
    AutoML reads the MLTable YAML to understand the schema.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Write the data as CSV
    csv_path = os.path.join(output_dir, "train.csv")
    df.to_csv(csv_path, index=False)

    # Write the MLTable YAML descriptor
    mltable_yaml = """$schema: https://azuremlschemas.azureedge.net/latest/MLTable.schema.json
type: mltable

paths:
  - file: ./train.csv

transformations:
  - read_delimited:
      delimiter: ","
      header: all_files_same_headers
      encoding: utf8
"""
    with open(os.path.join(output_dir, "MLTable"), "w") as f:
        f.write(mltable_yaml)


def main():
    args = parse_args()
    mlflow.start_run()

    # --- Load -----------------------------------------------------------------
    df = pd.read_csv(args.input_data)
    mlflow.log_metric("raw_rows", len(df))

    # --- Clean ----------------------------------------------------------------
    df = clean(df)
    mlflow.log_metric("clean_rows", len(df))

    # --- Split ----------------------------------------------------------------
    # IMPORTANT: Do NOT encode categoricals — AutoML handles featurization.
    # We only clean and split.
    train_df, test_df = train_test_split(
        df,
        test_size=args.test_size,
        random_state=args.random_seed,
        stratify=df["churn"],
    )
    mlflow.log_metric("train_rows", len(train_df))
    mlflow.log_metric("test_rows", len(test_df))

    # --- Write train as MLTable -----------------------------------------------
    write_mltable(train_df, args.output_train)

    # --- Write test as parquet ------------------------------------------------
    os.makedirs(args.output_test, exist_ok=True)
    test_df.to_parquet(os.path.join(args.output_test, "test.parquet"), index=False)

    mlflow.end_run()
    print(f"Data prep (AutoML) complete — train: {len(train_df)}, test: {len(test_df)}")


if __name__ == "__main__":
    main()
