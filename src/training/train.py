"""
Proximus Churn — Model Training
Trains a RandomForestClassifier on the prepared data and logs everything
(params, metrics, model artifact) with MLflow.
"""

import argparse
import os

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score


def parse_args():
    parser = argparse.ArgumentParser(description="Train churn model")
    parser.add_argument("--train-data", type=str, required=True, help="Path to train parquet dir")
    parser.add_argument("--model-output", type=str, required=True, help="Output dir for model artifact")
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--max-depth", type=int, default=10)
    parser.add_argument("--min-samples-split", type=int, default=5)
    parser.add_argument("--random-seed", type=int, default=42)
    return parser.parse_args()


def main():
    args = parse_args()
    mlflow.start_run()

    # --- Load -----------------------------------------------------------------
    train_df = pd.read_parquet(os.path.join(args.train_data, "train.parquet"))
    X_train = train_df.drop(columns=["churn"])
    y_train = train_df["churn"]

    # --- Train ----------------------------------------------------------------
    params = {
        "n_estimators": args.n_estimators,
        "max_depth": args.max_depth,
        "min_samples_split": args.min_samples_split,
        "random_state": args.random_seed,
        "class_weight": "balanced",
        "n_jobs": -1,
    }
    mlflow.log_params(params)

    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # --- Quick train-set metric (for sanity) ----------------------------------
    y_proba = model.predict_proba(X_train)[:, 1]
    train_auc = roc_auc_score(y_train, y_proba)
    mlflow.log_metric("train_auc", train_auc)

    # --- Log feature importances ----------------------------------------------
    feat_imp = pd.Series(model.feature_importances_, index=X_train.columns).sort_values(ascending=False)
    mlflow.log_text(feat_imp.head(15).to_string(), "feature_importances_top15.txt")

    # --- Save model -----------------------------------------------------------
    os.makedirs(args.model_output, exist_ok=True)
    mlflow.sklearn.save_model(model, args.model_output)
    mlflow.sklearn.log_model(model, artifact_path="churn-model")

    mlflow.end_run()
    print(f"Training complete — train AUC: {train_auc:.4f}")


if __name__ == "__main__":
    main()
