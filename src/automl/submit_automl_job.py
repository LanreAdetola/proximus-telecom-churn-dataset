"""
Submit AutoML Classification Job — Python SDK v2
=================================================

This script shows how to configure and submit the same AutoML job using the
Python SDK (azure-ai-ml). Useful for:
  - Notebook-based experimentation (exam topic: "Use notebooks for exploration")
  - Programmatic control over AutoML parameters
  - Understanding the SDK objects that map to the YAML config

Usage:
    python submit_automl_job.py

Prerequisites:
    pip install azure-ai-ml azure-identity
"""

from azure.ai.ml import MLClient, automl, Input
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential


def main():
    # ── 1. Connect to workspace ─────────────────────────────────────────────
    credential = DefaultAzureCredential()
    ml_client = MLClient(
        credential=credential,
        subscription_id="<your-subscription-id>",       # Replace
        resource_group_name="rg-proximus-mlops-dev",      # Your RG
        workspace_name="mlw-proximus-churn-dev",         # Your workspace
    )
    print(f"Connected to workspace: {ml_client.workspace_name}")

    # ── 2. Reference the registered data asset ──────────────────────────────
    # This points to azureml:churn-data-v1:1 which you already registered.
    training_data_input = Input(
        type=AssetTypes.URI_FILE,
        path="azureml:churn-data-v1:1",
    )

    # ── 3. Configure the AutoML classification job ──────────────────────────
    classification_job = automl.ClassificationJob(
        # Experiment identity
        experiment_name="proximus-churn-automl",
        display_name="automl-churn-sdk-submission",
        description="AutoML classification for Proximus churn (submitted via SDK)",

        # Compute
        compute="cpu-cluster",

        # Data
        training_data=training_data_input,
        target_column_name="churn",

        # Primary metric — what AutoML optimizes for
        primary_metric="AUC_weighted",

        # Validation strategy
        n_cross_validations=5,
    )

    # ── 4. Set featurization ────────────────────────────────────────────────
    # "auto" = AutoML decides encoding, imputation, scaling per column type
    classification_job.set_featurization(mode="auto")

    # ── 5. Set training parameters ──────────────────────────────────────────
    classification_job.set_training(
        blocked_training_algorithms=["TabNet", "MultinomialNaiveBayes"],
        enable_model_explainability=True,
        enable_vote_ensemble=True,
        enable_stack_ensemble=True,
        enable_onnx_compatible_models=False,
    )

    # ── 6. Set limits ───────────────────────────────────────────────────────
    classification_job.set_limits(
        timeout_minutes=60,
        trial_timeout_minutes=10,
        max_trials=20,
        max_concurrent_trials=2,
        enable_early_termination=True,
    )

    # ── 7. Submit the job ───────────────────────────────────────────────────
    returned_job = ml_client.jobs.create_or_update(classification_job)
    print(f"Job submitted: {returned_job.name}")
    print(f"Studio URL: {returned_job.studio_url}")

    # ── 8. (Optional) Wait for completion ───────────────────────────────────
    # Uncomment to block until the job finishes:
    # ml_client.jobs.stream(returned_job.name)

    # ── 9. After completion — get the best model ────────────────────────────
    # best_model = ml_client.jobs.get(returned_job.name).properties.get("best_child_run_id")
    # print(f"Best child run: {best_model}")


if __name__ == "__main__":
    main()
