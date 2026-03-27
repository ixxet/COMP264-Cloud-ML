# COMP 264 - Lab 3 Submission

Name: **Izzet Abidi**  
Course: **COMP 264 - Cloud Machine Learning**  
Lab: **Lab 3 - AWS Step Functions**  
Date: **2026-03-27**

## How to use this template

1. Follow `docs/RUN_ORDER.md` from top to bottom while working in AWS.
2. Every time you complete a step that matches `docs/SCREENSHOT_CHECKLIST.md`, save the screenshot using the exact filename from the checklist.
3. For Exercise 1, copy JSON from:
   - `exercise-1-step-functions-basics/snippets/pass_state_output.json`
   - `exercise-1-step-functions-basics/snippets/detect_sentiment_arguments.json`
   - `exercise-1-step-functions-basics/inputs/hello_world_true_wait_20.json`
   - `exercise-1-step-functions-basics/inputs/sentiment_analysis_input.json`
4. For Exercise 2, paste `exercise-2-step-functions-lambda/lambda_function.py` into the Lambda code editor, then use:
   - `exercise-2-step-functions-lambda/inputs/lambda_test_event.json`
   - `exercise-2-step-functions-lambda/inputs/state_machine_execution_input.json`
5. After the AWS work is finished, replace any text in square brackets below and keep the evidence filenames exactly as shown.

## Exercise 1 - Step Functions basics

### Do this during the lab

1. Create `MyFirstStateMachine` and save:
   - `02_myfirststatemachine_created.png`
2. Run the first execution `hello001` with no input and save:
   - `03_hello001_execution_success.png`
   - `04_pass_state_input_output.png`
3. Edit the first Pass state and paste:
   - `exercise-1-step-functions-basics/snippets/pass_state_output.json`
4. Save:
   - `05_external_input_output_snippet.png`
5. Start a new execution using:
   - `exercise-1-step-functions-basics/inputs/hello_world_true_wait_20.json`
6. Save:
   - `06_external_input_execution_success.png`
7. Add `DetectSentiment`, then paste:
   - `exercise-1-step-functions-basics/snippets/detect_sentiment_arguments.json`
8. Create the IAM role and inline policy from the tutorial and save:
   - `07_detect_sentiment_state_added.png`
   - `08_iam_role_and_policy.png`
9. Run the workflow with:
   - `exercise-1-step-functions-basics/inputs/sentiment_analysis_input.json`
10. Save:
   - `09_sentiment_execution_success.png`
   - `10_detect_sentiment_output.png`

I used the Step Functions getting-started workflow in Workflow Studio to create and run a state machine named `MyFirstStateMachine`.

### What I completed

- created the built-in Hello World state machine
- ran the initial execution
- reviewed graph, table, and input/output details
- updated the first Pass state to use external execution input
- added Amazon Comprehend `DetectSentiment`
- attached the required IAM role and policy
- ran the updated workflow successfully

### Evidence

- `01_stepfunctions_get_started_or_workflow_studio.png`
- `02_myfirststatemachine_created.png`
- `03_hello001_execution_success.png`
- `04_pass_state_input_output.png`
- `05_external_input_output_snippet.png`
- `06_external_input_execution_success.png`
- `07_detect_sentiment_state_added.png`
- `08_iam_role_and_policy.png`
- `09_sentiment_execution_success.png`
- `10_detect_sentiment_output.png`

### Notes

- State machine name used: `MyFirstStateMachine`
- IAM role used for Comprehend: `HelloWorldWorkflowRole`
- Inline policy used: `DetectSentimentPolicy`
- Input files used:
  - `exercise-1-step-functions-basics/inputs/hello_world_true_wait_20.json`
  - `exercise-1-step-functions-basics/inputs/sentiment_analysis_input.json`

## Exercise 2 - Step Functions that invoke Lambda

### Do this during the lab

1. Create a Python Lambda function named `HelloFunction`.
2. Replace the default code with:
   - `exercise-2-step-functions-lambda/lambda_function.py`
3. Deploy and save:
   - `11_hellofunction_created.png`
4. Test the function using:
   - `exercise-2-step-functions-lambda/inputs/lambda_test_event.json`
5. Save:
   - `12_lambda_test_success.png`
6. Create a blank Step Functions workflow and configure it to invoke `HelloFunction`.
7. Save:
   - `13_lambdastatemachine_configured.png`
8. Start execution using:
   - `exercise-2-step-functions-lambda/inputs/state_machine_execution_input.json`
9. Save:
   - `14_lambdastatemachine_execution_success.png`
   - `15_lambda_response_output.png`

I created an AWS Lambda function named `HelloFunction` and then created a single-step Step Functions workflow named `LambdaStateMachine` to invoke it.

### What I completed

- created and tested the Lambda function
- created a blank Step Functions workflow
- added the AWS Lambda Invoke API as the Task state
- configured the workflow to call `HelloFunction`
- started a Step Functions execution with JSON input
- verified successful output from Lambda

### Evidence

- `11_hellofunction_created.png`
- `12_lambda_test_success.png`
- `13_lambdastatemachine_configured.png`
- `14_lambdastatemachine_execution_success.png`
- `15_lambda_response_output.png`

### Notes

- Lambda function name: `HelloFunction`
- State machine name: `LambdaStateMachine`
- Both resources were kept in the same AWS account and AWS Region
- Code file used: `exercise-2-step-functions-lambda/lambda_function.py`
- Input files used:
  - `exercise-2-step-functions-lambda/inputs/lambda_test_event.json`
  - `exercise-2-step-functions-lambda/inputs/state_machine_execution_input.json`

## Cleanup

After capturing evidence, I cleaned up the resources created for the lab.

### Evidence

- `16_cleanup_resources.png`

### Direct instruction

After screenshots `01` through `15` are complete, delete the created Lambda function, state machines, and IAM roles if your instructor expects cleanup proof, then capture `16_cleanup_resources.png`.

## Conclusion

This lab demonstrated two Step Functions workflows:

- a visual Step Functions workflow that accepts external input and integrates with Amazon Comprehend
- a single-step Step Functions workflow that invokes AWS Lambda
