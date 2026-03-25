# Assignment 2 – Screenshot Checklist

Capture these screenshots at the specified points during execution. Name each file as indicated and include all screenshots in the analysis report.

## Required Screenshots

| # | Name | When to Capture | What Must Be Visible |
|---|------|----------------|---------------------|
| 1 | `screen1_izzet` | After notebook instance reaches InService | Instance name `izzetsession`, status `InService`, instance type `ml.t2.medium`, region `ca-central-1` |
| 2 | `screen2_izzet` | After training job completes | Training time output at the bottom of the `estimator.fit()` cell showing billable seconds and completion |
| 3 | `screen3_izzet` | After cleanup, in SageMaker Console | SageMaker > Training > Training Jobs page showing the completed training job |
| 4 | `screen4_izzet` | Click on the training job > View History | Training job history page with job details |
| 5 | `screen5_izzet` | Scroll to Monitor section > View Logs | CloudWatch log event for the training job (note which AWS service is shown) |
| 6 | `screen6_izzet` | Navigate to S3 > SageMaker bucket | The SageMaker-created bucket contents showing the demo prefix folder |
| 7 | `screen7_izzet` | Click into the demo prefix folder | Folder contents showing the data and xgboost-model subdirectories |

## Evidence Checklist

- [ ] All 7 screenshots captured with full browser window visible
- [ ] No partial screenshots (full window required)
- [ ] Screenshots named correctly: `screen1_izzet` through `screen7_izzet`
- [ ] All screenshots pasted into the analysis report
- [ ] Notebook downloaded as HTML: `izzet_income.html`
- [ ] Notebook downloaded as .ipynb for personal backup
- [ ] Demo video recorded (max 8 minutes) after cleanup
- [ ] Video named: `izzet_comp264_assignment#2_demo`
- [ ] Analysis report named: `izzet_comp264_assignment#2_analysis_report`
- [ ] Report includes: XGBoost algorithm research, SHAP research, all screenshots
- [ ] All files zipped as: `izzet_comp264_assignment#2.zip`

## Demo Video Plan (8 minutes max)

1. **Notebook walkthrough (4-5 min):** Open the notebook from your local machine. Walk through each step explaining what the code does and why.
2. **SageMaker Console (2-3 min):** Navigate to SageMaker Training Jobs, show the completed job, view history and CloudWatch logs. Navigate to S3 and show the model output bucket.
3. **Results discussion (1 min):** Summarize the model's accuracy, ROC AUC, and R² values.

## Analysis Report Sections

The analysis report should contain:
1. **Introduction** – Name, student ID, assignment objective
2. **Screenshots** – All 7 screenshots with brief descriptions
3. **XGBoost Research** – How the AWS implementation of XGBoost works (be thorough)
4. **SHAP Research** – What SHAP is and how it is used for model explainability
5. **Results** – Model metrics, observations about performance
6. **CloudWatch** – Note which AWS service is launched (visible in the log event)
