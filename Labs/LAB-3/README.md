# LAB-3 - AWS Step Functions

This folder is structured for COMP 264 Lab 3 and now matches the earlier lab layout.

Lab 3 is mostly AWS console work, so the local files here are meant to keep the process organized:

- `docs/`: run order, screenshot checklist, and a report template
- `exercise-1-step-functions-basics/`: copy-ready JSON inputs and snippets for the Step Functions getting-started exercise
- `exercise-2-step-functions-lambda/`: starter inputs and checklist for the Lambda integration exercise
- `screenshots/`: save your submission evidence here

## Source tutorials

Keep using these two AWS tutorial PDFs as the primary instructions locally:

- `Learn how to get started with Step Functions - AWS Step Functions.pdf`
- `Creating a Step Functions state machine that uses Lambda - AWS Step Functions.pdf`

They are reference material for your local workflow and are intentionally not meant to be committed into the GitHub repo.

## Recommended workflow

1. Stay in one AWS account and one AWS Region for both exercises.
2. Complete Exercise 1 first:
   `MyFirstStateMachine` -> external input -> `DetectSentiment`
3. Complete Exercise 2 second:
   `HelloFunction` -> `LambdaStateMachine`
4. Save screenshots as you go under `screenshots/exercise-1` and `screenshots/exercise-2`.
5. Fill in `docs/SUBMISSION_REPORT_TEMPLATE.md` after the AWS work is done.
6. Clean up IAM roles, state machines, Lambda functions, and any related resources after grading evidence is captured.

## Quick pointers

- State machine names cannot be renamed after creation.
- Execution names must be unique.
- For Exercise 2, keep the Lambda function and the Step Functions state machine in the same AWS account and AWS Region.
- For Exercise 1, the included JSON snippet files are there so you can paste them directly into Workflow Studio fields.
