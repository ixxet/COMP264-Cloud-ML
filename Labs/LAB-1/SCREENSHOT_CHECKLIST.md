# Screenshot Checklist

Use this as your evidence list for the lab submission.

## 1. SageMaker setup

Take a screenshot of the notebook instance creation page showing:

- AWS Region
- notebook instance name
- instance type `ml.t2.medium` or `ml.t3.medium`
- platform identifier `notebook-al2023-v1`
- IAM role selection

## 2. Notebook ready

Take a screenshot when the notebook instance status is `InService`.

## 3. Jupyter notebook

Take a screenshot of:

- the opened notebook
- the `conda_python3` kernel
- the uploaded files in the left file browser:
  `In_Class_Lab_1_SageMaker_Adult_Income.ipynb`,
  `sagemaker_adult_income_lab.py`,
  `adult.data`,
  `adult.test`

## 4. Data preparation

Run the preprocessing cells and capture:

- row counts before and after removing unknown values
- train / validation / test split counts
- generated artifact paths

## 5. S3 upload

Take one screenshot of either:

- the notebook output showing uploaded `train.csv` and `validation.csv`, or
- the S3 console showing those files under your lab prefix

## 6. Training job

Take a screenshot of the SageMaker training job page showing:

- training job name
- algorithm `xgboost`
- status `Completed`

If available, also capture the Debugger report link or output location.

## 7. Model deployment

Take a screenshot of the endpoint page showing:

- endpoint name
- instance type
- status `InService`

## 8. Model evaluation

Capture the notebook output showing:

- confusion matrix
- classification report
- ROC AUC
- best cutoff / minimum log loss
- the filled-in `Submission Summary` section, if possible

## 9. Optional SHAP explainability

If you run the optional SHAP section, capture:

- the SHAP summary plot
- the printed top features by mean absolute SHAP value

If your notebook saved the plots, also capture:

- `prediction_histogram.png`
- `log_loss_by_cutoff.png`

## 10. Cleanup

Take screenshots showing deletion or removal of:

- endpoint
- endpoint configuration
- model
- notebook instance
- S3 lab objects

If required by your instructor, also show CloudWatch `/aws/sagemaker/` log groups.

## Minimum evidence set

If you want the shortest acceptable set, capture these six:

1. notebook instance creation
2. notebook instance `InService`
3. notebook with successful preprocessing output
4. S3 upload confirmation
5. completed training job
6. deployed endpoint plus evaluation output
