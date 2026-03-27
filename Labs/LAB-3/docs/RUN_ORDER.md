# Run Order

Use this sequence to finish the lab with the least backtracking.

## 1. Prep

1. Sign in to AWS and switch to the exact AWS Region required by your course lab.
2. Open both services in the same browser session:
   - Step Functions
   - Lambda
3. Keep this folder open locally so you can copy JSON from the included files.

## 2. Exercise 1 - Step Functions basics

### Part A - Build and run the Hello World state machine

1. Open the Step Functions console and start the built-in Hello World workflow.
2. Create the state machine with:
   - Name: `MyFirstStateMachine`
   - Permissions: create a new role
3. Start the first execution:
   - Execution name: `hello001`
   - Input: leave empty
4. Review the execution graph, table view, and the first Pass state's input/output.

### Part B - Update it to accept external input

1. Edit the first Pass state output.
2. Paste the contents of:
   - `exercise-1-step-functions-basics/snippets/pass_state_output.json`
3. Save the state machine.
4. Start a new execution with:
   - Input file: `exercise-1-step-functions-basics/inputs/hello_world_true_wait_20.json`
5. Optional branch test:
   - Run again with `exercise-1-step-functions-basics/inputs/hello_world_false_wait_5.json`

### Part C - Add Amazon Comprehend DetectSentiment

1. Edit `MyFirstStateMachine`.
2. Add the `DetectSentiment` action to the default branch of the Choice state.
3. Remove the Fail state and end with Success.
4. In the DetectSentiment state arguments, paste:
   - `exercise-1-step-functions-basics/snippets/detect_sentiment_arguments.json`
5. Create and attach the IAM role and policy from the tutorial:
   - Role: `HelloWorldWorkflowRole`
   - Inline policy: `DetectSentimentPolicy`
6. Save the state machine and run it with:
   - `exercise-1-step-functions-basics/inputs/sentiment_analysis_input.json`
7. Review the DetectSentiment output and execution duration.

## 3. Exercise 2 - Step Functions with Lambda

### Part A - Create and test the Lambda function

1. Open the Lambda console.
2. Create a function:
   - Name: `HelloFunction`
3. If you use Python, paste:
   - `exercise-2-step-functions-lambda/lambda_function.py`
4. Deploy the function.
5. Test it with:
   - `exercise-2-step-functions-lambda/inputs/lambda_test_event.json`
6. Copy the Lambda function ARN.

### Part B - Create the Step Functions workflow

1. Open the Step Functions console.
2. Create a blank state machine in Workflow Studio.
3. Add the AWS Lambda Invoke API as the first state.
4. Select the `HelloFunction` Lambda function.
5. Keep the default payload behavior.
6. Name the state machine:
   - `LambdaStateMachine`
7. Create the workflow and confirm role creation.

### Part C - Run it

1. Start execution for `LambdaStateMachine`.
2. Use:
   - `exercise-2-step-functions-lambda/inputs/state_machine_execution_input.json`
3. Confirm the execution succeeds and the Lambda response is visible in the output.

## 4. Capture evidence

Follow:

- `docs/SCREENSHOT_CHECKLIST.md`

## 5. Finish the write-up

Fill in:

- `docs/SUBMISSION_REPORT_TEMPLATE.md`

## 6. Cleanup

Delete or remove the following after your screenshots are complete:

- `MyFirstStateMachine`
- `LambdaStateMachine`
- `HelloFunction`
- `HelloWorldWorkflowRole`
- any Step Functions auto-created execution role you no longer need
