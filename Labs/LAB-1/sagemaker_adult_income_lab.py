from __future__ import annotations

import os
import zipfile
from pathlib import Path
from typing import Any

import boto3
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn import metrics
from sklearn.model_selection import train_test_split


RAW_COLUMNS = [
    "age",
    "workclass",
    "fnlwgt",
    "education",
    "education_num",
    "marital_status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "capital_gain",
    "capital_loss",
    "hours_per_week",
    "native_country",
    "income",
]

# The AWS tutorial uses SHAP's cleaned Adult dataset, which omits these two columns.
MODEL_FEATURES = [
    "age",
    "workclass",
    "education_num",
    "marital_status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "capital_gain",
    "capital_loss",
    "hours_per_week",
    "native_country",
]

CATEGORICAL_FEATURES = [
    "workclass",
    "marital_status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "native_country",
]

NUMERIC_FEATURES = [
    "age",
    "education_num",
    "capital_gain",
    "capital_loss",
    "hours_per_week",
]

TARGET_COLUMN = "income_over_50k"
RANDOM_STATE = 1

WORK_DIR = Path(
    os.environ.get(
        "LAB_WORK_DIR",
        str(Path(__file__).resolve().parent / "artifacts"),
    )
)

RUN_SAGEMAKER_PIPELINE = os.environ.get("RUN_SAGEMAKER_PIPELINE", "false").lower() == "true"
DEPLOY_ENDPOINT = os.environ.get("DEPLOY_ENDPOINT", "false").lower() == "true"
RUN_BATCH_TRANSFORM = os.environ.get("RUN_BATCH_TRANSFORM", "false").lower() == "true"
ENABLE_DEBUGGER_RULES = os.environ.get("ENABLE_DEBUGGER_RULES", "true").lower() == "true"

S3_PREFIX = os.environ.get("S3_PREFIX", "in-class-lab-1/adult-income-xgboost")
TRAIN_INSTANCE_TYPE = os.environ.get("SAGEMAKER_TRAIN_INSTANCE", "ml.m4.xlarge")
ENDPOINT_INSTANCE_TYPE = os.environ.get("SAGEMAKER_ENDPOINT_INSTANCE", "ml.t2.medium")
BATCH_INSTANCE_TYPE = os.environ.get("SAGEMAKER_BATCH_INSTANCE", "ml.m4.xlarge")
XGBOOST_VERSION = os.environ.get("SAGEMAKER_XGBOOST_VERSION", "1.2-1")


def resolve_dataset_paths() -> tuple[Path, Path]:
    explicit_train = os.environ.get("ADULT_TRAIN_PATH")
    explicit_test = os.environ.get("ADULT_TEST_PATH")
    if explicit_train and explicit_test:
        return Path(explicit_train), Path(explicit_test)

    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / "adult",
        script_dir,
        Path("/home/ec2-user/SageMaker/Labs/LAB-1/adult"),
        Path("/home/ec2-user/SageMaker/Labs/LAB-1"),
        Path("/home/ec2-user/SageMaker/adult"),
        Path("/home/ec2-user/SageMaker"),
        Path("/Users/zizo/Downloads"),
        Path("/Users/zizo/Downloads/adult"),
    ]

    for candidate in candidates:
        train_path = candidate / "adult.data"
        test_path = candidate / "adult.test"
        if train_path.exists() and test_path.exists():
            return train_path, test_path

        zip_path = candidate / "adult.zip"
        if zip_path.exists():
            extract_dir = candidate / "adult"
            extract_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path, "r") as archive:
                archive.extractall(extract_dir)

            extracted_train = extract_dir / "adult.data"
            extracted_test = extract_dir / "adult.test"
            if extracted_train.exists() and extracted_test.exists():
                print(f"Extracted {zip_path} to {extract_dir}")
                return extracted_train, extracted_test

    raise FileNotFoundError(
        "Could not find adult.data and adult.test. "
        "Place them beside the script, inside an `adult/` subfolder, upload "
        "`adult.zip`, or set ADULT_TRAIN_PATH and ADULT_TEST_PATH."
    )


def load_adult_dataframe(train_path: Path, test_path: Path) -> pd.DataFrame:
    train_df = pd.read_csv(
        train_path,
        names=RAW_COLUMNS,
        header=None,
        skipinitialspace=True,
        na_values="?",
    )
    test_df = pd.read_csv(
        test_path,
        names=RAW_COLUMNS,
        header=None,
        skiprows=1,
        skipinitialspace=True,
        na_values="?",
    )

    for frame in (train_df, test_df):
        text_columns = frame.select_dtypes(include="object").columns
        for column in text_columns:
            frame[column] = frame[column].str.strip()

    test_df["income"] = test_df["income"].str.rstrip(".")
    combined = pd.concat([train_df, test_df], ignore_index=True)

    rows_before = len(combined)
    combined = combined.dropna().reset_index(drop=True)
    print(f"Loaded {rows_before} rows from raw files.")
    print(f"Dropped {rows_before - len(combined)} rows containing unknown values.")
    print(f"Working with {len(combined)} clean rows.")

    return combined


def build_features(clean_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    prepared = clean_df.copy()
    prepared[TARGET_COLUMN] = (prepared["income"] == ">50K").astype(int)

    display_features = prepared[MODEL_FEATURES].copy()
    encoded_features = pd.get_dummies(
        display_features,
        columns=CATEGORICAL_FEATURES,
        dtype=int,
    )
    labels = prepared[TARGET_COLUMN].copy()

    print(f"Encoded feature matrix shape: {encoded_features.shape}")
    print(f"Positive class rate: {labels.mean():.4f}")

    return encoded_features, labels, display_features


def split_dataset(
    features: pd.DataFrame,
    labels: pd.Series,
) -> dict[str, pd.DataFrame | pd.Series]:
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=labels,
    )
    x_train, x_val, y_train, y_val = train_test_split(
        x_train,
        y_train,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=y_train,
    )

    print(f"Train rows: {len(x_train)}")
    print(f"Validation rows: {len(x_val)}")
    print(f"Test rows: {len(x_test)}")

    return {
        "x_train": x_train,
        "x_val": x_val,
        "x_test": x_test,
        "y_train": y_train,
        "y_val": y_val,
        "y_test": y_test,
    }


def label_first_frame(labels: pd.Series, features: pd.DataFrame) -> pd.DataFrame:
    return pd.concat(
        [
            labels.reset_index(drop=True).rename(TARGET_COLUMN).astype(int),
            features.reset_index(drop=True),
        ],
        axis=1,
    )


def save_exploration_plots(display_features: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    axes = display_features[NUMERIC_FEATURES].hist(
        bins=30,
        sharey=True,
        figsize=(16, 8),
    )
    for axis in axes.flatten():
        axis.set_ylabel("count")
    plt.tight_layout()
    plot_path = output_dir / "numeric_feature_histograms.png"
    plt.savefig(plot_path)
    plt.close()
    print(f"Saved histogram plot to {plot_path}")


def write_local_artifacts(splits: dict[str, pd.DataFrame | pd.Series], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    train_frame = label_first_frame(splits["y_train"], splits["x_train"])
    validation_frame = label_first_frame(splits["y_val"], splits["x_val"])
    test_frame = label_first_frame(splits["y_test"], splits["x_test"])

    train_path = output_dir / "train.csv"
    validation_path = output_dir / "validation.csv"
    test_features_path = output_dir / "test.csv"
    test_labeled_path = output_dir / "test_with_labels.csv"

    train_frame.to_csv(train_path, index=False, header=False)
    validation_frame.to_csv(validation_path, index=False, header=False)
    splits["x_test"].to_csv(test_features_path, index=False, header=False)
    test_frame.to_csv(test_labeled_path, index=False, header=False)

    print(f"Wrote {train_path}")
    print(f"Wrote {validation_path}")
    print(f"Wrote {test_features_path}")
    print(f"Wrote {test_labeled_path}")

    return {
        "train": train_path,
        "validation": validation_path,
        "test_features": test_features_path,
        "test_with_labels": test_labeled_path,
    }


def require_sagemaker() -> Any:
    try:
        import sagemaker
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The SageMaker Python SDK is not installed. "
            "Install it with `pip install -qU sagemaker` before running the AWS stages."
        ) from exc
    return sagemaker


def resolve_execution_role() -> str:
    sagemaker = require_sagemaker()
    try:
        return sagemaker.get_execution_role()
    except ValueError:
        role_arn = os.environ.get("SAGEMAKER_EXECUTION_ROLE_ARN")
        if role_arn:
            return role_arn
        raise RuntimeError(
            "No SageMaker execution role found. "
            "If you are not running inside a SageMaker notebook instance, "
            "set SAGEMAKER_EXECUTION_ROLE_ARN first."
        )


def upload_to_s3(bucket: str, prefix: str, artifacts: dict[str, Path]) -> dict[str, str]:
    s3 = boto3.Session().resource("s3")
    uploaded = {}

    for channel, local_path in artifacts.items():
        key = f"{prefix}/data/{local_path.name}"
        s3.Bucket(bucket).Object(key).upload_file(str(local_path))
        uploaded[channel] = f"s3://{bucket}/{key}"
        print(f"Uploaded {local_path} -> {uploaded[channel]}")

    return uploaded


def build_estimator(
    session: Any,
    role: str,
    region: str,
    bucket: str,
    prefix: str,
) -> Any:
    sagemaker = require_sagemaker()
    from sagemaker.debugger import ProfilerRule, Rule, rule_configs

    image_uri = sagemaker.image_uris.retrieve("xgboost", region, XGBOOST_VERSION)
    output_path = f"s3://{bucket}/{prefix}/xgboost-model"

    estimator_kwargs = {
        "image_uri": image_uri,
        "role": role,
        "instance_count": 1,
        "instance_type": TRAIN_INSTANCE_TYPE,
        "volume_size": 5,
        "output_path": output_path,
        "sagemaker_session": session,
    }

    if ENABLE_DEBUGGER_RULES:
        estimator_kwargs["rules"] = [
            Rule.sagemaker(rule_configs.create_xgboost_report()),
            ProfilerRule.sagemaker(rule_configs.ProfilerReport()),
        ]

    estimator = sagemaker.estimator.Estimator(**estimator_kwargs)
    estimator.set_hyperparameters(
        max_depth=5,
        eta=0.2,
        gamma=4,
        min_child_weight=6,
        subsample=0.7,
        objective="binary:logistic",
        num_round=1000,
    )
    return estimator


def predict_batches(
    predictor: Any,
    feature_frame: pd.DataFrame,
    rows: int = 1000,
) -> np.ndarray:
    split_arrays = np.array_split(feature_frame.to_numpy(), int(feature_frame.shape[0] / float(rows) + 1))
    predictions = ""
    for array in split_arrays:
        if len(array) == 0:
            continue
        response = predictor.predict(array).decode("utf-8")
        predictions = ",".join([predictions, response])
    return np.fromstring(predictions[1:], sep=",")


def evaluate_predictions(
    predictions: np.ndarray,
    y_true: pd.Series,
    output_dir: Path,
) -> dict[str, float]:
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))
    plt.hist(predictions, bins=30)
    plt.title("Predicted probabilities")
    plt.xlabel("prediction")
    plt.ylabel("count")
    prediction_histogram_path = output_dir / "prediction_histogram.png"
    plt.tight_layout()
    plt.savefig(prediction_histogram_path)
    plt.close()

    cutoff = 0.5
    hard_predictions = np.where(predictions > cutoff, 1, 0)
    confusion = metrics.confusion_matrix(y_true, hard_predictions)
    report = metrics.classification_report(y_true, hard_predictions)
    auc = metrics.roc_auc_score(y_true, predictions)
    accuracy = metrics.accuracy_score(y_true, hard_predictions)

    print("Confusion matrix at cutoff 0.5:")
    print(confusion)
    print("Classification report at cutoff 0.5:")
    print(report)
    print(f"ROC AUC: {auc:.4f}")
    print(f"Accuracy at cutoff 0.5: {accuracy:.4f}")

    cutoffs = np.arange(0.01, 1.0, 0.01)
    log_losses = [
        metrics.log_loss(y_true, np.where(predictions > current_cutoff, 1, 0))
        for current_cutoff in cutoffs
    ]

    plt.figure(figsize=(12, 6))
    plt.plot(cutoffs, log_losses)
    plt.title("Log loss by cutoff")
    plt.xlabel("cutoff")
    plt.ylabel("log loss")
    cutoff_plot_path = output_dir / "log_loss_by_cutoff.png"
    plt.tight_layout()
    plt.savefig(cutoff_plot_path)
    plt.close()

    best_index = int(np.argmin(log_losses))
    best_cutoff = float(cutoffs[best_index])
    min_log_loss = float(log_losses[best_index])

    print(f"Best cutoff by log loss: {best_cutoff:.2f}")
    print(f"Minimum log loss: {min_log_loss:.4f}")
    print(f"Saved prediction histogram to {prediction_histogram_path}")
    print(f"Saved cutoff plot to {cutoff_plot_path}")

    return {
        "accuracy_at_0_5": float(accuracy),
        "roc_auc": float(auc),
        "best_cutoff": best_cutoff,
        "min_log_loss": min_log_loss,
    }


def run_batch_transform(
    estimator: Any,
    batch_input_uri: str,
    batch_output_uri: str,
) -> None:
    transformer = estimator.transformer(
        instance_count=1,
        instance_type=BATCH_INSTANCE_TYPE,
        output_path=batch_output_uri,
    )
    transformer.transform(
        data=batch_input_uri,
        data_type="S3Prefix",
        content_type="text/csv",
        split_type="Line",
    )
    transformer.wait()
    print(f"Batch transform output saved under {batch_output_uri}")


def main() -> None:
    train_path, test_path = resolve_dataset_paths()

    print("Starting Adult Income SageMaker lab workflow")
    print(f"Train source: {train_path}")
    print(f"Test source: {test_path}")
    print(f"Output directory: {WORK_DIR}")

    clean_df = load_adult_dataframe(train_path, test_path)
    feature_matrix, labels, display_features = build_features(clean_df)
    save_exploration_plots(display_features, WORK_DIR)

    splits = split_dataset(feature_matrix, labels)
    local_artifacts = write_local_artifacts(splits, WORK_DIR)

    if not RUN_SAGEMAKER_PIPELINE:
        print("\nLocal preprocessing completed.")
        print("Set RUN_SAGEMAKER_PIPELINE=true to upload, train, and continue with SageMaker.")
        return

    sagemaker = require_sagemaker()
    from sagemaker.serializers import CSVSerializer
    from sagemaker.session import TrainingInput

    session = sagemaker.Session()
    region = session.boto_region_name
    if not region:
        raise RuntimeError("AWS region is not configured. Set AWS_REGION before running SageMaker steps.")

    role = resolve_execution_role()
    bucket = session.default_bucket()

    print(f"AWS region: {region}")
    print(f"SageMaker role: {role}")
    print(f"Default bucket: {bucket}")

    s3_artifacts = upload_to_s3(bucket, S3_PREFIX, local_artifacts)
    estimator = build_estimator(session, role, region, bucket, S3_PREFIX)

    train_input = TrainingInput(s3_artifacts["train"], content_type="csv")
    validation_input = TrainingInput(s3_artifacts["validation"], content_type="csv")

    estimator.fit({"train": train_input, "validation": validation_input}, wait=True)
    print(f"Training job name: {estimator.latest_training_job.job_name}")
    print(f"Model artifact: {estimator.model_data}")

    if not DEPLOY_ENDPOINT:
        print("\nTraining completed.")
        print("Set DEPLOY_ENDPOINT=true to deploy the model and run hosted endpoint evaluation.")
        return

    predictor = estimator.deploy(
        initial_instance_count=1,
        instance_type=ENDPOINT_INSTANCE_TYPE,
        serializer=CSVSerializer(),
    )
    print(f"Endpoint name: {predictor.endpoint_name}")

    predictions = predict_batches(predictor, splits["x_test"])
    metrics_summary = evaluate_predictions(predictions, splits["y_test"], WORK_DIR)
    print(f"Evaluation summary: {metrics_summary}")

    if RUN_BATCH_TRANSFORM:
        batch_output_uri = f"s3://{bucket}/{S3_PREFIX}/batch-prediction"
        run_batch_transform(estimator, s3_artifacts["test_features"], batch_output_uri)

    print("\nCleanup when finished:")
    print(f"1. Delete endpoint {predictor.endpoint_name}")
    print("2. Delete the endpoint configuration and model in SageMaker")
    print(f"3. Remove S3 objects under s3://{bucket}/{S3_PREFIX}/")


if __name__ == "__main__":
    main()
