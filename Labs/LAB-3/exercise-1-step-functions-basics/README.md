# Exercise 1 - Step Functions basics

This folder contains the small JSON assets you can paste into the Step Functions console while following the AWS getting-started tutorial.

## Included files

- `inputs/hello_world_true_wait_20.json`: execution input for the external-input success path
- `inputs/hello_world_false_wait_5.json`: optional branch test input
- `inputs/sentiment_analysis_input.json`: execution input for the Comprehend sentiment example
- `snippets/pass_state_output.json`: paste into the first Pass state's Output field
- `snippets/detect_sentiment_arguments.json`: paste into the DetectSentiment state's Arguments field

## Recommended names from the tutorial

- state machine: `MyFirstStateMachine`
- IAM role for Comprehend: `HelloWorldWorkflowRole`
- inline policy: `DetectSentimentPolicy`

## How to use this folder

1. Build the Hello World state machine in Step Functions.
2. Run the initial execution with no input.
3. Edit the first Pass state and paste `snippets/pass_state_output.json`.
4. Start a new execution using `inputs/hello_world_true_wait_20.json`.
5. Add `DetectSentiment`, then paste `snippets/detect_sentiment_arguments.json`.
6. Create and attach the IAM role and inline policy.
7. Run again with `inputs/sentiment_analysis_input.json`.
