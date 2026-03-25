"""
COMP 264 Assignment 2 – SageMaker XGBoost Adult Income Prediction
Izzet Abidi (300898230)

Standalone script that mirrors the izzet_income.ipynb notebook logic.
Supports local preprocessing and optional SageMaker training/deployment.

Usage:
    # local preprocessing only
    python izzet_income_sagemaker.py

    # full SageMaker pipeline
    RUN_SAGEMAKER_PIPELINE=true DEPLOY_ENDPOINT=true python izzet_income_sagemaker.py
"""

from __future__ import annotations

import os
from pathlib import Path

import boto3
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn import metrics
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RAW_COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education_num",
    "marital_status", "occupation", "relationship", "race", "sex",
    "capital_gain", "capital_loss", "hours_per_week", "native_country", "income",
]

MODEL_FEATURES = [
    "age", "workclass", "education_num", "marital_status", "occupation",
    "relationship", "race", "sex", "capital_gain", "capital_loss",
    "hours_per_week", "native_country",
]

CATEGORICAL_FEATURES = [
    "workclass", "marital_status", "occupation", "relationship",
    "race", "sex", "native_country",
]

NUMERIC_FEATURES = [
    "age", "education_num", "capital_gain", "capital_loss", "hours_per_week",
]

TARGET_COLUMN = "income_over_50k"
PREFIX = "demo-sage-maker-xgboost-izzet"
RANDOM_STATE = 1

WORK_DIR = Path(os.environ.get("LAB_WORK_DIR", str(Path(__file__).resolve().parent / "artifacts")))

RUN_SAGEMAKER_PIPELINE = os.environ.get("RUN_SAGEMAKER_PIPELINE", "false").lower() == "true"
DEPLOY_ENDPOINT = os.environ.get("DEPLOY_ENDPOINT", "false").lower() == "true"


# ---------------------------------------------------------------------------
# Data Loading and Preprocessing
# ---------------------------------------------------------------------------

def load_dataset() -> pd.DataFrame:
    """Load and clean the UCI Adult Income dataset."""
    script_dir = Path(__file__).resolve().parent
    candidates = [script_dir, script_dir / "adult", Path.cwd()]

    train_path = test_path = None
    for candidate in candidates:
        t = candidate / "adult.data"
        e = candidate / "adult.test"
        if t.exists() and e.exists():
            train_path, test_path = t, e
            break

    if not train_path:
        raise FileNotFoundError(
            "Could not find adult.data and adult.test. "
            "Place them beside this script or in an adult/ subfolder."
        )

    train_df = pd.read_csv(
        train_path, names=RAW_COLUMNS, header=None,
        skipinitialspace=True, na_values="?",
    )
    test_df = pd.read_csv(
        test_path, names=RAW_COLUMNS, header=None,
        skiprows=1, skipinitialspace=True, na_values="?",
    )

    for frame in (train_df, test_df):
        for col in frame.select_dtypes(include="object").columns:
            frame[col] = frame[col].str.strip()

    test_df["income"] = test_df["income"].str.rstrip(".")

    combined = pd.concat([train_df, test_df], ignore_index=True)
    rows_before = len(combined)
    combined = combined.dropna().reset_index(drop=True)

    print(f"Loaded {rows_before} rows from raw files.")
    print(f"Dropped {rows_before - len(combined)} rows with unknown values.")
    print(f"Working with {len(combined)} clean rows.")

    return combined


def build_features(df: pd.DataFrame):
    """Create target variable and encode features."""
    df[TARGET_COLUMN] = (df["income"] == ">50K").astype(int)

    print("Prefix name:", PREFIX)
    print("Target variable type:", type(df[TARGET_COLUMN]))
    print("Target variable dtype:", df[TARGET_COLUMN].dtype)
    print("Target variable size:", len(df[TARGET_COLUMN]))
    print("Class value counts:")
    print(df[TARGET_COLUMN].value_counts())

    features = pd.get_dummies(df[MODEL_FEATURES], columns=CATEGORICAL_FEATURES, dtype=int)
    labels = df[TARGET_COLUMN]

    print(f"\nEncoded feature matrix shape: {features.shape}")
    print(f"Positive class rate: {labels.mean():.4f}")

    return features, labels


def split_and_save(features, labels):
    """Split dataset and write SageMaker-format CSVs."""
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, random_state=RANDOM_STATE, stratify=labels,
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.25, random_state=RANDOM_STATE, stratify=y_train,
    )

    print(f"Train rows:      {len(X_train)}")
    print(f"Validation rows: {len(X_val)}")
    print(f"Test rows:       {len(X_test)}")

    WORK_DIR.mkdir(parents=True, exist_ok=True)

    def label_first(lab, feat):
        return pd.concat([
            lab.reset_index(drop=True).rename(TARGET_COLUMN).astype(int),
            feat.reset_index(drop=True),
        ], axis=1)

    for name, lab, feat in [
        ("train.csv", y_train, X_train),
        ("validation.csv", y_val, X_val),
    ]:
        label_first(lab, feat).to_csv(WORK_DIR / name, index=False, header=False)
        print(f"Wrote {WORK_DIR / name}")

    X_test.to_csv(WORK_DIR / "test.csv", index=False, header=False)
    print(f"Wrote {WORK_DIR / 'test.csv'}")

    return {
        "X_train": X_train, "X_val": X_val, "X_test": X_test,
        "y_train": y_train, "y_val": y_val, "y_test": y_test,
    }


# ---------------------------------------------------------------------------
# SageMaker Pipeline
# ---------------------------------------------------------------------------

def run_sagemaker(splits):
    """Upload data, train, deploy, evaluate, and clean up."""
    import sagemaker
    from sagemaker.serializers import CSVSerializer
    from sagemaker.session import TrainingInput

    session = sagemaker.Session()
    region = session.boto_region_name
    role = sagemaker.get_execution_role()
    bucket = session.default_bucket()

    print(f"AWS Region: {region}")
    print(f"Role ARN: {role}")
    print(f"Default bucket: {bucket}")

    # upload to S3
    s3 = boto3.Session().resource("s3")
    s3_uris = {}
    for name in ["train.csv", "validation.csv", "test.csv"]:
        key = f"{PREFIX}/data/{name}"
        s3.Bucket(bucket).Object(key).upload_file(str(WORK_DIR / name))
        s3_uris[name] = f"s3://{bucket}/{key}"
        print(f"Uploaded {name} -> {s3_uris[name]}")

    # configure estimator with assignment hyperparameters
    image_uri = sagemaker.image_uris.retrieve("xgboost", region, "1.2-1")
    output_path = f"s3://{bucket}/{PREFIX}/xgboost-model"

    estimator = sagemaker.estimator.Estimator(
        image_uri=image_uri,
        role=role,
        instance_count=1,
        instance_type="ml.m4.xlarge",
        volume_size=5,
        output_path=output_path,
        sagemaker_session=session,
    )

    estimator.set_hyperparameters(
        max_depth=4,
        eta=0.25,
        gamma=4,
        min_child_weight=4,
        subsample=0.7,
        objective="binary:logistic",
        num_round=500,
    )

    # train
    train_input = TrainingInput(s3_uris["train.csv"], content_type="csv")
    val_input = TrainingInput(s3_uris["validation.csv"], content_type="csv")
    estimator.fit({"train": train_input, "validation": val_input}, wait=True)

    print(f"Training job: {estimator.latest_training_job.job_name}")
    print(f"Model artifact: {estimator.model_data}")

    if not DEPLOY_ENDPOINT:
        print("Training complete. Set DEPLOY_ENDPOINT=true to deploy and evaluate.")
        return

    # deploy
    predictor = estimator.deploy(
        initial_instance_count=1,
        instance_type="ml.t2.medium",
        serializer=CSVSerializer(),
    )
    print(f"Endpoint: {predictor.endpoint_name}")

    # predict
    X_test = splits["X_test"]
    y_test = splits["y_test"]
    split_arrays = np.array_split(X_test.to_numpy(), max(1, len(X_test) // 1000))
    raw_predictions = ""
    for arr in split_arrays:
        if len(arr) == 0:
            continue
        resp = predictor.predict(arr).decode("utf-8")
        raw_predictions = ",".join([raw_predictions, resp])
    predictions = np.fromstring(raw_predictions[1:], sep=",")

    # evaluate
    hard_preds = np.where(predictions > 0.5, 1, 0)
    print("Confusion Matrix:")
    print(metrics.confusion_matrix(y_test, hard_preds))
    print("\nClassification Report:")
    print(metrics.classification_report(y_test, hard_preds))
    print(f"Accuracy: {metrics.accuracy_score(y_test, hard_preds):.4f}")
    print(f"ROC AUC: {metrics.roc_auc_score(y_test, predictions):.4f}")
    print(f"R-squared: {r2_score(y_test, predictions):.4f}")

    # cleanup
    print("\nCleanup when finished:")
    print(f"1. Delete endpoint: {predictor.endpoint_name}")
    print(f"2. Remove S3 objects under s3://{bucket}/{PREFIX}/")
    print("3. Stop and delete the notebook instance")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("COMP 264 Assignment 2 – SageMaker XGBoost")
    print("Izzet Abidi (300898230)")
    print("=" * 60)

    df = load_dataset()
    features, labels = build_features(df)

    # exploration plot
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    df[NUMERIC_FEATURES].hist(bins=30, sharey=True, figsize=(16, 8))
    plt.tight_layout()
    plt.savefig(WORK_DIR / "numeric_feature_histograms.png")
    plt.close()
    print(f"Saved histograms to {WORK_DIR / 'numeric_feature_histograms.png'}")

    splits = split_and_save(features, labels)

    if RUN_SAGEMAKER_PIPELINE:
        run_sagemaker(splits)
    else:
        print("\nLocal preprocessing complete.")
        print("Set RUN_SAGEMAKER_PIPELINE=true to continue with SageMaker.")


if __name__ == "__main__":
    main()
