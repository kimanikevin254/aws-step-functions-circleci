import json
import os
from typing import Any

import boto3  # type: ignore
import dotenv
from loguru import logger

dotenv.load_dotenv()

STATE_MACHINE_NAME = os.getenv("STATE_MACHINE_NAME")
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID")

sf_client = boto3.client("stepfunctions", region_name=AWS_REGION)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Handle S3 event and trigger Step Functions execution."""
    try:
        # Get the S3 bucket and key from the event
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]

        # Prepare input for Step Functions
        input_data = {
            "document_id": key.split("/")[-1].split(".")[0],  # Extract filename without extension
            "s3_path": f"s3://{bucket}/{key}",
        }

        # Start Step Functions execution
        response = sf_client.start_execution(
            stateMachineArn=f"arn:aws:states:{AWS_REGION}:{AWS_ACCOUNT_ID}:stateMachine:{STATE_MACHINE_NAME}",
                        input=json.dumps(input_data),
        )

        logger.info(f"Started Step Functions execution: {response['executionArn']}")
        return {"statusCode": 200, "body": "Step Functions execution started successfully"}

    except Exception as e:
        logger.error(f"Error processing S3 event: {e}")
        raise