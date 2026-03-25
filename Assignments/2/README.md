# Assignment 2 – Machine Learning on the Cloud

**Course:** COMP 264 – Cloud ML
**Weight:** 100%
**Due:** Friday, Week 12
**Student:** Izzet Abidi (300898230)

---

## 1. Overview

This assignment trains, deploys, and evaluates a binary classification model using Amazon SageMaker. The model predicts whether an individual earns more than $50K per year based on demographic features from the UCI Adult Census Income dataset. It builds on the AWS service integration skills from Assignment 1 by introducing the full machine learning lifecycle: data preparation, cloud-based training, real-time deployment, and model evaluation.

## 2. Exercise Breakdown

### Exercise: Train a Machine Learning Model Using Amazon SageMaker (100%)

**Objective:** Use SageMaker's built-in XGBoost algorithm to train a binary classifier on the Adult Income dataset with custom hyperparameters.

**What the notebook does:**
1. Installs and configures the SageMaker SDK
2. Loads the Adult Census dataset (`adult.data` and `adult.test`)
3. Cleans the data by removing rows with unknown values and stripping whitespace
4. Creates a binary target variable (`income_over_50k`)
5. One-hot encodes categorical features into numeric columns
6. Splits into 60% train / 20% validation / 20% test (stratified)
7. Writes SageMaker-format CSVs (label in first column, no header)
8. Uploads CSV files to S3 under the `demo-sage-maker-xgboost-izzet` prefix
9. Configures XGBoost with assignment-specified hyperparameters
10. Launches a SageMaker training job on `ml.m4.xlarge`
11. Deploys the trained model to a real-time endpoint on `ml.t2.medium`
12. Sends test data to the endpoint in batches and collects predictions
13. Computes confusion matrix, classification report, ROC AUC, accuracy, and R²
14. Cleans up the endpoint and S3 objects

**Hyperparameters (as specified in assignment):**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `max_depth` | 4 | Maximum tree depth |
| `eta` | 0.25 | Learning rate |
| `gamma` | 4 | Minimum loss reduction for split |
| `min_child_weight` | 4 | Minimum sum of instance weight in child |
| `subsample` | 0.7 | Row sampling ratio per tree |
| `objective` | binary:logistic | Binary classification with probability output |
| `num_round` | 500 | Number of boosting rounds |

**File manifest:**

| File | Purpose |
|------|---------|
| `izzet_income.ipynb` | Primary Jupyter notebook for SageMaker execution |
| `izzet_income_sagemaker.py` | Standalone Python script mirroring notebook logic |
| `README.md` | This documentation file |
| `SCREENSHOT_CHECKLIST.md` | Evidence collection guide |

## 3. Runbook

### Prerequisites

- AWS account with SageMaker access (SSO login, not root)
- Region set to **Canada (Central) – ca-central-1**
- IAM role with SageMaker execution permissions
- Adult dataset files: `adult.data` and `adult.test` from [UCI ML Repository](https://archive.ics.uci.edu/ml/datasets/adult)

### Execution: SageMaker Notebook

```bash
# 1. Log into AWS Console via SSO
# 2. Navigate to SageMaker > Notebook Instances
# 3. Create notebook instance named "izzetsession" (ml.t2.medium)
# 4. Once InService, click "Open Jupyter"
# 5. Upload izzet_income.ipynb, adult.data, adult.test
# 6. Set kernel to conda_python3
# 7. Run all cells sequentially
# 8. After evaluation, run cleanup cells
# 9. Stop and delete the notebook instance
```

### Execution: Local Preprocessing Only

```bash
# place adult.data and adult.test beside the script
python izzet_income_sagemaker.py
```

### Execution: Full Pipeline (from SageMaker)

```bash
RUN_SAGEMAKER_PIPELINE=true DEPLOY_ENDPOINT=true python izzet_income_sagemaker.py
```

### Troubleshooting

| Issue | Fix |
|-------|-----|
| `ResourceLimitExceeded` on ml.m4.xlarge | Request a service quota increase or use ml.m5.large |
| Notebook kernel dies during training | Training continues in SageMaker; reconnect and check `estimator.latest_training_job` |
| Endpoint creation timeout | Wait longer; `ml.t2.medium` endpoints take 5-10 minutes |
| `NoSuchBucket` error | Verify region is set to ca-central-1 before creating the session |

## 4. Expected Results

- **Dataset size:** ~45,222 clean rows after removing unknowns
- **Class balance:** ~24% positive (>50K), ~76% negative (<=50K)
- **Accuracy:** Expected range 0.84–0.87 at cutoff 0.5
- **ROC AUC:** Expected range 0.89–0.92
- **R²:** Typically 0.35–0.50 (lower than regression tasks since this is binary classification)
- **Training time:** ~3-5 minutes on ml.m4.xlarge with 500 rounds

## 5. Topics Learned

**Data Preparation**
- Dataset cleaning — removing missing values and normalizing text fields
- Feature encoding — one-hot encoding categorical variables for tree-based models
- SageMaker data format — label-first CSV without headers

**Cloud ML Infrastructure**
- SageMaker notebook instances — managed Jupyter environments with IAM roles
- S3 integration — uploading training data and retrieving model artifacts
- Training jobs — managed containers running built-in algorithms
- Real-time endpoints — deploying models for online inference

**Model Training and Evaluation**
- XGBoost hyperparameter tuning — understanding the effect of depth, learning rate, and regularization
- Classification metrics — confusion matrix, precision, recall, F1, ROC AUC
- R-squared for classification — interpreting variance explained by probability predictions
- Cutoff optimization — finding the threshold that minimizes log loss

**AWS Cost Management**
- Resource cleanup — deleting endpoints, S3 objects, and notebook instances to prevent charges
- Instance selection — choosing appropriate instance types for training vs. inference

## 6. Definitions and Key Concepts

| Term | Definition |
|------|-----------|
| Amazon SageMaker | Managed AWS service for building, training, and deploying ML models |
| Notebook Instance | An EC2 instance running Jupyter managed by SageMaker |
| Execution Role | IAM role that grants SageMaker permissions to access AWS resources |
| S3 Bucket | Object storage used for training data, model artifacts, and outputs |
| XGBoost | Extreme Gradient Boosting; an ensemble tree-based ML algorithm |
| Gradient Boosting | Technique that builds trees sequentially, each correcting prior errors |
| Hyperparameter | Configuration value set before training that controls model behavior |
| max_depth | Maximum number of levels in each decision tree |
| eta (learning rate) | Step size shrinkage to prevent overfitting |
| gamma | Minimum loss reduction required to make a further partition |
| min_child_weight | Minimum sum of instance weight needed in a child node |
| subsample | Fraction of training rows sampled per boosting round |
| num_round | Total number of boosting iterations |
| Binary Classification | Predicting one of two classes (>50K or <=50K) |
| One-Hot Encoding | Converting categorical values into binary indicator columns |
| Stratified Split | Preserving class proportions across train/validation/test sets |
| Confusion Matrix | Table showing true positives, false positives, true negatives, false negatives |
| ROC AUC | Area under the Receiver Operating Characteristic curve; measures discrimination |
| R-squared | Proportion of variance in the target explained by the model |
| Log Loss | Measures the distance between predicted probabilities and true labels |
| Real-Time Endpoint | A deployed model that serves predictions via HTTP requests |
| CSVSerializer | SageMaker serializer that formats input as CSV for the XGBoost container |
| Training Job | A SageMaker-managed process that runs model training on specified instances |
| Model Artifact | The trained model file (tar.gz) stored in S3 after training completes |
| SHAP | SHapley Additive exPlanations; a method for interpreting feature importance |
| CloudWatch Logs | AWS logging service that captures SageMaker training and endpoint logs |

## 7. Potential Improvements and Industry Considerations

### Approach Comparison

| Category | Assignment Approach | Industry Alternative | Trade-Off |
|----------|-------------------|---------------------|-----------|
| Hyperparameter Tuning | Manual (fixed values) | SageMaker Automatic Model Tuning (Bayesian optimization) | Manual is reproducible and cheap; AMT finds better parameters at higher cost |
| Feature Engineering | One-hot encoding only | Target encoding, feature interactions, embeddings | One-hot is transparent; advanced encoding risks leakage without careful CV |
| Model Selection | Single XGBoost model | Ensemble of XGBoost + LightGBM + neural network | Single model is interpretable; ensembles add marginal accuracy at complexity cost |
| Deployment | Real-time endpoint | Batch Transform or Serverless Inference | Real-time suits low-latency needs; batch is cheaper for bulk scoring |
| Monitoring | None | SageMaker Model Monitor for data drift and prediction quality | Monitoring is essential in production but overkill for one-time assignments |
| Explainability | Optional SHAP section | SHAP integrated into production pipeline with feature attribution logs | SHAP adds trust and debuggability; adds inference latency |

### Where the Baseline Still Holds Up

- **Fixed hyperparameters** are appropriate when the goal is learning the SageMaker workflow rather than maximizing accuracy. The assignment-specified values produce strong results without the cost of hyperparameter search jobs.
- **One-hot encoding** is the correct default for tree-based models on datasets with moderate cardinality. The Adult dataset's categorical features have at most ~40 unique values, well within the range where one-hot works without dimensionality problems.
- **ml.t2.medium for inference** is the right choice for a demo endpoint that serves occasional test requests. Production workloads would need larger instances or auto-scaling, but the cost savings here prevent unnecessary AWS charges during the assignment.
