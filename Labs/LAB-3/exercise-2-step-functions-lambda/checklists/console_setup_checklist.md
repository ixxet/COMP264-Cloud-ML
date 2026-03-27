# Console setup checklist

## Lambda

1. Open the Lambda console.
2. Create a Python function from scratch named `HelloFunction`.
3. Replace the default handler code with `../lambda_function.py`, then choose Deploy.
4. Test the function with `../inputs/lambda_test_event.json`.
5. Confirm the output contains a `greeting` built from the `who` field.
6. Copy the Lambda ARN.

## Step Functions

1. Open the Step Functions console.
2. Create a blank state machine.
3. Add the AWS Lambda Invoke API as the first state.
4. Select `HelloFunction`.
5. Keep the default payload selection.
6. Name the state machine `LambdaStateMachine`.
7. Create the workflow and confirm role creation.
8. Start execution with `../inputs/state_machine_execution_input.json`.
9. Confirm the execution succeeds and the Lambda response is visible in the output.
