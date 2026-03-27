# Lab 3 Screenshot Checklist

Save screenshots under:

- `screenshots/exercise-1/`
- `screenshots/exercise-2/`

## Exercise 1 - Step Functions basics

1. `01_stepfunctions_get_started_or_workflow_studio.png`
- Show the Step Functions getting-started screen or Workflow Studio entry point.

2. `02_myfirststatemachine_created.png`
- Show `MyFirstStateMachine` after creation.

3. `03_hello001_execution_success.png`
- Show the first execution succeeding.

4. `04_pass_state_input_output.png`
- Show the first Pass state's input/output with generated variables.

5. `05_external_input_output_snippet.png`
- Show the edited Pass state output using `exercise-1-step-functions-basics/snippets/pass_state_output.json`.

6. `06_external_input_execution_success.png`
- Show execution using `hello_world_true_wait_20.json`.

7. `07_detect_sentiment_state_added.png`
- Show the workflow with `DetectSentiment` added.

8. `08_iam_role_and_policy.png`
- Show `HelloWorldWorkflowRole` and the inline `DetectSentimentPolicy`.

9. `09_sentiment_execution_success.png`
- Show successful execution using `exercise-1-step-functions-basics/inputs/sentiment_analysis_input.json`.

10. `10_detect_sentiment_output.png`
- Show the DetectSentiment task output or execution details.

## Exercise 2 - Step Functions with Lambda

11. `11_hellofunction_created.png`
- Show the Lambda function `HelloFunction` with `exercise-2-step-functions-lambda/lambda_function.py` pasted into the code editor.

12. `12_lambda_test_success.png`
- Show a successful Lambda test result using `exercise-2-step-functions-lambda/inputs/lambda_test_event.json`.

13. `13_lambdastatemachine_configured.png`
- Show the Step Functions workflow configured to invoke `HelloFunction`.

14. `14_lambdastatemachine_execution_success.png`
- Show a successful Step Functions execution using `exercise-2-step-functions-lambda/inputs/state_machine_execution_input.json`.

15. `15_lambda_response_output.png`
- Show the execution output that includes the Lambda response, especially the `greeting` field.

## Cleanup

16. `16_cleanup_resources.png`
- Show cleanup or deletion for the created Lambda function, state machines, and IAM roles if your instructor expects proof.

## Minimum evidence set

If you want a shorter acceptable set, capture at least these:

1. `MyFirstStateMachine` created
2. first Hello World execution success
3. external-input execution success
4. DetectSentiment execution success
5. Lambda function test success
6. `LambdaStateMachine` execution success
