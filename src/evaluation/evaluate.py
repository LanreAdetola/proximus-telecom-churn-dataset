"""
Proximus Churn — Model Evaluation
Loads the trained model and test set, computes classification metrics,
and logs results with MLflow.
"""

import argparse
import json
import os

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate churn model")
    parser.add_argument("--model-input", type=str, required=True, help="Path to saved model dir")
    parser.add_argument("--test-data", type=str, required=True, help="Path to test parquet dir")
    parser.add_argument("--evaluation-output", type=str, required=True, help="Output dir for eval results")
    return parser.parse_args()


def main():
    args = parse_args()
    mlflow.start_run()

    # --- Load model + test data -----------------------------------------------
    model = mlflow.sklearn.load_model(args.model_input)
    test_df = pd.read_parquet(os.path.join(args.test_data, "test.parquet"))

    X_test = test_df.drop(columns=["churn"])
    y_test = test_df["churn"]

    # --- Predict --------------------------------------------------------------
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # --- Metrics --------------------------------------------------------------
    metrics = {
        "test_auc": roc_auc_score(y_test, y_proba),
        "test_accuracy": accuracy_score(y_test, y_pred),
        "test_precision": precision_score(y_test, y_pred),
        "test_recall": recall_score(y_test, y_pred),
        "test_f1": f1_score(y_test, y_pred),
    }

    for name, value in metrics.items():
        mlflow.log_metric(name, value)

    # --- Classification report ------------------------------------------------
    report = classification_report(y_test, y_pred, target_names=["No Churn", "Churn"])
    mlflow.log_text(report, "classification_report.txt")

    # --- Write eval results to output dir -------------------------------------
    os.makedirs(args.evaluation_output, exist_ok=True)
    with open(os.path.join(args.evaluation_output, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    mlflow.end_run()

    print("Evaluation complete:")
    for name, value in metrics.items():
        print(f"  {name}: {value:.4f}")


if __name__ == "__main__":
    main()
