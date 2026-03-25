# COMP 264 – Cloud ML

Izzet Abidi (300898230) | Centennial College | AI – Software Engineering Technology | Winter 2025

---

## Repository Structure

```
ML_Work/
├── Assignments/
│   ├── 1/                          Assignment 1 – AWS Services Integration
│   │   ├── izzet_filesuplolad.py       Exercise 1: S3 file upload (boto3)
│   │   ├── assignment1_ex2_commands.sh  Exercise 2: Comprehend entity extraction
│   │   ├── izzet_speaking_pictorial/    Exercise 3: Polly text-to-speech translator
│   │   └── diagrams/                   Architecture diagrams (Mermaid)
│   └── 2/                          Assignment 2 – SageMaker ML Training
│       ├── izzet_income.ipynb          SageMaker XGBoost notebook
│       └── izzet_income_sagemaker.py   Standalone script
├── in class lab 1/                 In-Class Lab – SageMaker XGBoost Pipeline
│   ├── In_Class_Lab_1_SageMaker_Adult_Income.ipynb
│   └── sagemaker_adult_income_lab.py
└── README.md
```

## Assignments

| # | Title | AWS Services | Core Skill |
|---|-------|-------------|------------|
| 1 | AWS Services Integration | S3, Comprehend, Comprehend Medical, Rekognition, Translate, Polly | Programmatic interaction with cloud AI services |
| 2 | SageMaker ML Training | SageMaker, S3, XGBoost | End-to-end ML model lifecycle on the cloud |

| Lab | Title | AWS Services | Core Skill |
|-----|-------|-------------|------------|
| In-Class 1 | SageMaker XGBoost Pipeline | SageMaker, S3 | Data preparation, training, deployment, evaluation |

## Course Progression

This repository traces a path from basic AWS service calls to full machine learning pipelines on the cloud:

**Phase 1 – Service Integration (Assignment 1)**
Establishes the ability to interact with AWS programmatically. Starts with file storage (S3 + boto3), introduces NLP services (Comprehend for entity extraction), and builds a multi-service application chaining computer vision (Rekognition), translation (Translate), and speech synthesis (Polly) through a serverless Chalice API.

**Phase 2 – ML Pipeline (In-Class Lab 1 → Assignment 2)**
Shifts from consuming pre-built AI services to training custom models. The in-class lab introduces the SageMaker workflow end-to-end: data preprocessing, S3 staging, XGBoost training, endpoint deployment, and evaluation. Assignment 2 applies the same pipeline with custom hyperparameters, adds required evaluation metrics (R²), and emphasizes cost-conscious resource management.

### Building Blocks

Each phase builds on the previous:

```
Assignment 1                          Assignment 2
─────────────                         ─────────────
boto3 SDK usage          ──────────>  S3 data staging for training
S3 file operations       ──────────>  Model artifact storage
AWS CLI commands         ──────────>  SageMaker CLI/SDK integration
Service chaining         ──────────>  ML pipeline orchestration
Chalice REST API         ──────────>  Endpoint deployment and inference
Error handling           ──────────>  Resource cleanup and cost control
```

## Technology Stack

| Technology | Purpose | Used In |
|-----------|---------|---------|
| boto3 | AWS SDK for Python | All |
| AWS Chalice | Serverless REST API framework | Assignment 1 |
| Amazon S3 | Object storage | All |
| Amazon Comprehend | NLP entity extraction | Assignment 1 |
| Amazon Comprehend Medical | PHI detection | Assignment 1 |
| Amazon Rekognition | Image text detection | Assignment 1 |
| Amazon Translate | Neural machine translation | Assignment 1 |
| Amazon Polly | Text-to-speech synthesis | Assignment 1 |
| Amazon SageMaker | ML training and deployment | In-Class Lab 1, Assignment 2 |
| XGBoost | Gradient boosting classifier | In-Class Lab 1, Assignment 2 |
| pandas | Data manipulation | Assignment 2, In-Class Lab 1 |
| scikit-learn | Evaluation metrics and splitting | Assignment 2, In-Class Lab 1 |
| matplotlib | Visualization | Assignment 2, In-Class Lab 1 |
| SHAP | Model explainability | In-Class Lab 1 |

## Running the Repository

### Assignment 1

```bash
# Exercise 1: S3 file upload
cd Assignments/1
python3 izzet_filesuplolad.py --bucket <your-bucket>

# Exercise 2: Entity extraction
./assignment1_ex2_commands.sh "Your text here"

# Exercise 3: Speaking Pictorial
cd izzet_speaking_pictorial
chalice local
# Open frontend/index.html in a browser
```

### Assignment 2

```bash
# Option A: Run on SageMaker notebook instance
# Upload izzet_income.ipynb + adult.data + adult.test to SageMaker
# Run all cells in conda_python3 kernel

# Option B: Local preprocessing only
cd Assignments/2
python3 izzet_income_sagemaker.py
```

### In-Class Lab 1

```bash
cd "in class lab 1"
python3 sagemaker_adult_income_lab.py
# Set RUN_SAGEMAKER_PIPELINE=true for full AWS pipeline
```

## Industry Context

The skills developed across this coursework map directly to production ML engineering roles:

- **Service Integration (Assignment 1)** mirrors building AI-powered features into applications — the same pattern used by companies embedding translation, OCR, and voice capabilities into products via managed API services.
- **ML Pipeline (Assignment 2)** follows the standard model development lifecycle used in production: data versioning in S3, managed training infrastructure, model registry, endpoint deployment, and metric-driven evaluation. The emphasis on cleanup and cost management reflects real-world cloud budget discipline.
- **XGBoost on SageMaker** remains one of the most common production ML patterns for tabular data, used extensively in fraud detection, credit scoring, and customer churn prediction.
