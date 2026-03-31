# Azure AutoML — Proximus Churn Classification

## What This Adds to Your Repo

```
├── jobs/
│   └── automl-churn-classification.yml    ← Standalone AutoML job (simplest)
├── pipelines/
│   └── automl-churn-pipeline.yml          ← AutoML as a pipeline step (MLOps-aligned)
├── src/
│   ├── automl/
│   │   └── submit_automl_job.py           ← SDK v2 submission script (for notebooks)
│   └── data_prep_automl/
│       └── prep_automl.py                 ← Data prep that outputs MLTable format
└── .github/workflows/
    └── run-automl.yml                     ← CI/CD workflow for AutoML
```

## Quick Start

### Option A: Standalone Job (fastest to try)

```bash
az ml job create --file jobs/automl-churn-classification.yml
```

This submits AutoML directly against your registered `churn-data-v1:1` data asset.
No data prep step — AutoML handles featurization internally.

### Option B: Pipeline (production-aligned)

```bash
az ml job create --file pipelines/automl-churn-pipeline.yml
```

This runs data_prep → AutoML → (you can add evaluation after).
Data prep outputs MLTable format, which AutoML requires as a pipeline input.

### Option C: SDK v2 (for notebooks)

```python
python src/automl/submit_automl_job.py
```

Edit the subscription/RG/workspace placeholders first.

---

## Key AutoML Parameters Explained (Exam-Critical)

### task
The ML problem type. Options: `classification`, `regression`, `forecasting`.
Your churn column is Yes/No → `classification`.

### primary_metric
What AutoML optimizes. For classification:
- `AUC_weighted` — best for imbalanced classes (recommended for churn)
- `accuracy` — misleading when classes are imbalanced
- `precision_score_weighted`, `recall_score_weighted`, `f1_score_weighted`
- `norm_macro_recall` — normalized macro-averaged recall

### featurization.mode
- `auto` — AutoML detects column types and applies appropriate transforms
  (one-hot encoding, target encoding, missing value imputation, text features, date features)
- `custom` — you specify per-column overrides
- `off` — no featurization (you pre-process everything yourself)

### training.blocked_training_algorithms
List of algorithms AutoML should NOT try. Useful to skip slow/unsuitable ones.
For 1K rows, blocking `TabNet` (deep learning) is sensible.

### training.enable_model_explainability
When `true`, AutoML generates feature importance for the best model using
model-agnostic explainers. This ties to the exam topic "Evaluate a model
by using responsible AI principles."

### training.enable_vote_ensemble / enable_stack_ensemble
- VotingEnsemble: combines top models by weighted voting
- StackEnsemble: trains a meta-learner on top model outputs
These often produce the best overall performance but are slower to train.

### limits
| Parameter | What It Controls |
|---|---|
| `timeout_minutes` | Total wall-clock time for the entire AutoML job |
| `trial_timeout_minutes` | Max time per individual algorithm trial |
| `max_trials` | Max number of algorithm+hyperparameter combos to try |
| `max_concurrent_trials` | Parallel trials (must be ≤ cluster max nodes) |
| `enable_early_termination` | Bandit policy — stops unpromising trials early |

### n_cross_validations
Number of CV folds. AutoML uses this to evaluate each trial internally.
- Datasets < 20K rows → use k-fold CV (e.g., 5)
- Datasets > 20K rows → consider a train/validation split instead

### validation_data / validation_data_size
Alternative to CV: provide a separate validation set or specify a percentage split.

---

## Exam Pitfalls and Best Practices

### Pitfall 1: MLTable vs URI File
- **Standalone AutoML job** → can accept `uri_file` directly (AutoML reads the CSV)
- **AutoML as a pipeline step** → requires `mltable` format for `training_data`
- The prep_automl.py script handles this by writing both the CSV and the MLTable YAML

### Pitfall 2: max_concurrent_trials > cluster nodes
If you set `max_concurrent_trials: 4` but your cluster has `max_node_count: 2`,
only 2 trials run at a time. The exam may test whether you understand this link.

### Pitfall 3: Featurization before AutoML
Do NOT one-hot encode categoricals before passing data to AutoML with `featurization: auto`.
AutoML applies its own encoding and may double-encode your features.
The prep_automl.py script intentionally skips encoding (unlike your standard prep.py).

### Pitfall 4: Primary metric for imbalanced data
If churn rate is ~20%, using `accuracy` as primary_metric is misleading (a model
predicting "No" always gets 80% accuracy). Use `AUC_weighted` or `f1_score_weighted`.

### Pitfall 5: Early termination
`enable_early_termination: true` applies a Bandit policy that terminates trials
whose primary metric falls below the best trial by a configurable slack.
This saves compute cost but may miss a slow-converging model.

---

## After AutoML Completes

### View Results in Azure ML Studio
Navigate to: Experiments → proximus-churn-automl → click the run → Models tab.
You'll see all trials ranked by primary_metric with:
- Algorithm name
- Hyperparameters used
- All metrics (AUC, accuracy, F1, precision, recall)
- Feature importance (if explainability was enabled)

### Register the Best Model
```bash
# Get the best child run ID from the parent AutoML job
az ml job show --name <automl-job-name> --query properties.best_child_run_id

# Register the best model
az ml model create \
  --name churn-automl-best \
  --version 1 \
  --path azureml://jobs/<best-child-run-id>/outputs/mlflow-model \
  --type mlflow_model
```

### Compare with Your Manual Pipeline
Your existing RandomForest pipeline logs `test_auc` to MLflow.
AutoML logs `AUC_weighted` across CV folds.
Use the Azure ML Studio "Compare" feature to compare the best AutoML model
against your manually tuned RandomForest — this covers the exam topic
"Compare model performance across jobs."
