# Exercise 2 - Step Functions with Lambda

This folder contains a sample Lambda handler, starter inputs, and a console checklist for the Lambda integration exercise.

## Included files

- `lambda_function.py`: paste-ready Python Lambda handler for `HelloFunction`
- `inputs/lambda_test_event.json`: use when testing the Lambda function directly
- `inputs/state_machine_execution_input.json`: use when starting the Step Functions execution
- `checklists/console_setup_checklist.md`: fast reference for the AWS console steps

## Recommended names from the tutorial

- Lambda function: `HelloFunction`
- Step Functions state machine: `LambdaStateMachine`

## Important constraint

Keep the Lambda function and the Step Functions state machine in the same AWS account and AWS Region.

## Notes

- The fastest path is to create `HelloFunction` with a Python runtime, then paste `lambda_function.py` into the Lambda code editor and deploy it.
- The JSON input files here are runtime-agnostic. They work whether you author the Lambda function in Python, Node.js, or another supported runtime.
- The Step Functions workflow is a single Task state that invokes Lambda through Workflow Studio.
