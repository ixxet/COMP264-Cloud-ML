# In Class Lab 1

This folder contains a complete SageMaker XGBoost workflow for the Adult Census Income dataset.

`adult.zip` is only the bundled copy of the same raw UCI files. The script uses the unpacked files directly:

- `/Users/zizo/Downloads/adult/adult.data`
- `/Users/zizo/Downloads/adult/adult.test`
- `/Users/zizo/Downloads/adult/adult.names`

## Files

- `In_Class_Lab_1_SageMaker_Adult_Income.ipynb`: native SageMaker notebook version.
- `sagemaker_adult_income_lab.py`: end-to-end lab workflow.
- `SCREENSHOT_CHECKLIST.md`: evidence checklist for submission.
- `artifacts/`: generated locally after you run the script.

## What is different from the AWS tutorial

The AWS tutorial loads a pre-cleaned SHAP version of Adult Census data. Your local files are the original raw UCI files, so this workflow adds the preprocessing that the tutorial does not show:

- removes rows with unknown values (`?`)
- strips the trailing `.` from test labels
- mirrors the tutorial feature set by dropping `fnlwgt` and the string `education` column
- one-hot encodes categorical columns so SageMaker built-in XGBoost receives numeric CSV data

## AWS prerequisites

1. Change to the AWS Region required by your lab before creating resources.
2. Create a SageMaker notebook instance:
   `ml.t2.medium` or `ml.t3.medium` if `t2` is unavailable.
3. Set the platform identifier to `notebook-al2023-v1`.
4. Use the `conda_python3` kernel.
5. Make sure the SageMaker execution role can create and tag SageMaker resources.

If you run outside a SageMaker notebook instance, also set:

```bash
export SAGEMAKER_EXECUTION_ROLE_ARN="arn:aws:iam::<account-id>:role/<your-sagemaker-role>"
```

## Recommended file upload choice

Use unpacked files if possible.

- Recommended: upload `adult.data` and `adult.test` directly.
- Supported: upload `adult.zip` instead. The helper script can extract it automatically.

Why unpacked is better:

- easier to confirm the files are in the notebook instance
- easier to show in screenshots
- fewer moving parts during the lab

## AWS console steps

Use this sequence inside AWS:

1. Open the SageMaker AI console.
2. In the top-right region selector, switch to the exact region your lab requires.
3. In the left navigation, open `Notebook instances`.
4. Choose `Create notebook instance`.
5. Set:
   `Notebook instance name` to your lab name,
   `Notebook instance type` to `ml.t2.medium` or `ml.t3.medium`,
   `Platform identifier` to `notebook-al2023-v1`.
6. For `IAM role`, choose `Create a new role`, then create the role.
7. Create the notebook instance and wait until the status becomes `InService`.
8. Open the instance with `Open JupyterLab` or `Open Jupyter`.
9. Create a new notebook using the `conda_python3` kernel, or upload and open `In_Class_Lab_1_SageMaker_Adult_Income.ipynb`.
10. Upload `sagemaker_adult_income_lab.py` and either:
    `adult.data` plus `adult.test`, or `adult.zip`.

Important clarification:

- There is no separate SageMaker AI `import dataset` button needed for this notebook workflow.
- The notebook reads the local dataset files first, then uploads the processed CSV files to Amazon S3 for training.
- To verify the uploaded training data, open the Amazon S3 console and inspect the bucket/prefix printed by the notebook output.

## Local preprocessing only

This is the safest first run. It verifies the dataset and writes the CSV files SageMaker expects.

```bash
cd "/Users/zizo/Documents/Centennial/School/3402/Sem6/264 - Cloud ML/ML_Work/Labs/LAB-1"
python3 sagemaker_adult_income_lab.py
```

That creates:

- `artifacts/train.csv`
- `artifacts/validation.csv`
- `artifacts/test.csv`
- `artifacts/test_with_labels.csv`
- `artifacts/numeric_feature_histograms.png`

## Full SageMaker run

If you are running this on your local machine with AWS credentials configured:

```bash
cd "/Users/zizo/Documents/Centennial/School/3402/Sem6/264 - Cloud ML/ML_Work/Labs/LAB-1"
export AWS_REGION="us-east-1"
export RUN_SAGEMAKER_PIPELINE="true"
python3 sagemaker_adult_income_lab.py
```

To continue all the way through endpoint deployment and hosted evaluation:

```bash
export DEPLOY_ENDPOINT="true"
python3 sagemaker_adult_income_lab.py
```

Optional batch transform:

```bash
export RUN_BATCH_TRANSFORM="true"
python3 sagemaker_adult_income_lab.py
```

## Running inside the SageMaker notebook instance

1. Upload the notebook and helper script into the notebook instance folder.
2. Upload either:
   `adult.data` and `adult.test`, or `adult.zip`.
3. If needed, install or update the SageMaker SDK:

```bash
pip install -qU sagemaker
```

4. Optional but recommended if you want an explainability section at the end of the notebook:

```bash
pip install -q shap xgboost
```

The notebook does not require SHAP for training or deployment. SHAP is only used at the end to explain feature influence in a more professional way.

5. Open and run [In_Class_Lab_1_SageMaker_Adult_Income.ipynb](/Users/zizo/Documents/Centennial/School/3402/Sem6/264%20-%20Cloud%20ML/ML_Work/Labs/LAB-1/In_Class_Lab_1_SageMaker_Adult_Income.ipynb) from top to bottom.
6. When the notebook prints the default bucket and uploads the CSV files, open the Amazon S3 console, go to that bucket, and navigate to the printed prefix ending in `/data/` to confirm `train.csv` and `validation.csv` exist.
7. After training finishes, deploy the endpoint, run the evaluation cell, and fill in the final `Submission Summary` markdown cell.
8. If you want a stronger report, run the optional SHAP section at the end and capture the SHAP feature-importance output.

## If you prefer running the Python script directly in SageMaker

The notebook is the recommended path for the assignment, but the script also works in a SageMaker notebook instance terminal.

```bash
export RUN_SAGEMAKER_PIPELINE="true"
export DEPLOY_ENDPOINT="true"
python3 sagemaker_adult_income_lab.py
```

## Notes

- Training uses the same built-in SageMaker XGBoost image version shown in the AWS getting-started tutorial: `1.2-1`.
- Training defaults to `ml.m4.xlarge`, matching the tutorial. Change it with `SAGEMAKER_TRAIN_INSTANCE` if your lab environment requires a different instance family.
- Deployment defaults to `ml.t2.medium`, matching the tutorial notebook endpoint step.
- SageMaker resources cost money while they are running.

## Cleanup

Delete these after your screenshots and validation are done:

1. SageMaker endpoint
2. SageMaker endpoint configuration
3. SageMaker model
4. SageMaker notebook instance
5. S3 objects under your lab prefix
6. CloudWatch log groups that start with `/aws/sagemaker/`
