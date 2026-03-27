"""Sample Lambda handler for COMP 264 Lab 3 Exercise 2."""


def lambda_handler(event, context):
    event = event or {}
    who = event.get("who", "World")

    # Keep the response structured so the Step Functions output is easy to review.
    return {
        "greeting": f"Hello, {who}!",
        "received_input": event,
    }
