import json
import os
import time
from typing import Any

import boto3
import dotenv  # type: ignore
from loguru import logger

dotenv.load_dotenv()

AWS_REGION = os.environ["AWS_REGION"]
AWS_ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID"]
SF_ROLE_NAME = os.environ["SF_ROLE_NAME"]
LAMBDA_ROLE_NAME = os.environ["LAMBDA_ROLE_NAME"]
LAMBDA_FOLDER = os.environ["LAMBDA_FOLDER"]
LAMBDA_FUNCTION_ONE = os.environ["LAMBDA_FUNCTION_ONE"]
LAMBDA_FUNCTION_TWO = os.environ["LAMBDA_FUNCTION_TWO"]
LAMBDA_FUNCTION_S3_TRIGGER = os.environ["LAMBDA_FUNCTION_S3_TRIGGER"]
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
STATE_MACHINE_NAME = os.environ["STATE_MACHINE_NAME"]

s3_client = boto3.client("s3", region_name=AWS_REGION)
lambda_client = boto3.client("lambda", region_name=AWS_REGION)
sf_client = boto3.client("stepfunctions", region_name=AWS_REGION)


def create_lambda_function(name: str, zip_path: str, role_arn: str, handler: str) -> str:
    """Create or update a Lambda function."""
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"{zip_path} does not exist. Make sure to zip your code first.")

    with open(zip_path, "rb") as f:
        zipped_code = f.read()

    try:
        lambda_client.get_function(FunctionName=name)
        logger.info(f"✅ Lambda function {name} already exists. Updating code...")
        response = lambda_client.update_function_code(FunctionName=name, ZipFile=zipped_code)
    except lambda_client.exceptions.ResourceNotFoundException:
        logger.info(f"🚀 Creating new Lambda function {name}...")
        response = lambda_client.create_function(
            FunctionName=name,
            Runtime="python3.12",
            Role=role_arn,
            Handler=handler,
            Code={"ZipFile": zipped_code},
            Timeout=10,
            Environment={"Variables": {
                    "STATE_MACHINE_NAME": STATE_MACHINE_NAME,
                    "AWS_ACCOUNT_ID": AWS_ACCOUNT_ID,
                }
            },
        )

    return str(response["FunctionArn"])


def deploy_state_machine(
    def_path: str, role_arn: str, lambdas: dict[str, str], state_machine_name: str = str(STATE_MACHINE_NAME)
) -> dict[str, Any]:
    with open(def_path) as f:
        definition = json.load(f)

    # Convert JSON object to string
    definition_str = json.dumps(definition)

    # Replace placeholders with real Lambda ARNs
    definition_str = definition_str.replace("TASK_ONE_LAMBDA_ARN", lambdas["TaskOne"])
    definition_str = definition_str.replace("TASK_TWO_LAMBDA_ARN", lambdas["TaskTwo"])

    # Now deploy
    existing_machines = sf_client.list_state_machines()["stateMachines"]
    logger.info(f"Found {len(existing_machines)} existing state machines.")
    logger.info(f"Existing machines: {existing_machines}")

    state_machine_arn = None
    for sm in existing_machines:
        if sm["name"] == state_machine_name:
            state_machine_arn = sm["stateMachineArn"]
            break

    if state_machine_arn:
        logger.info(f"✅ State Machine {state_machine_name} already exists. Updating...")
        response = sf_client.update_state_machine(
            stateMachineArn=state_machine_arn, definition=definition_str, roleArn=role_arn
        )
    else:
        logger.info(f"🚀 Creating new State Machine {state_machine_name}...")
        response = sf_client.create_state_machine(
            name=state_machine_name, definition=definition_str, roleArn=role_arn, type="STANDARD"
        )

    return dict(response)


def add_lambda_permission(function_name: str, bucket_name: str) -> None:
    """Add permission for S3 to invoke the Lambda function."""
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=f"S3InvokeFunction-{bucket_name}",  # Unique statement ID
            Action="lambda:InvokeFunction",
            Principal="s3.amazonaws.com",
            SourceArn=f"arn:aws:s3:::{bucket_name}",
        )
        logger.info(f"Added S3 invoke permission to Lambda function {function_name}")
    except lambda_client.exceptions.ResourceConflictException:
        logger.info(f"Permission already exists for Lambda function {function_name}")


def add_s3_trigger_to_bucket(bucket_name: str, lambda_arn: str) -> None:
    """Configure S3 bucket to trigger Lambda on file upload."""
    function_name = lambda_arn.split(":")[-1]

    add_lambda_permission(function_name, bucket_name)

    # Wait for a few seconds to ensure the permission is propagated
    logger.info("Waiting for permission propagation...")
    time.sleep(5)

    try:
        s3_client.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration={
                "LambdaFunctionConfigurations": [{"LambdaFunctionArn": lambda_arn, "Events": ["s3:ObjectCreated:*"]}]
            },
        )
        logger.info(f"Added S3 trigger configuration to bucket {bucket_name}")
    except Exception as e:
        logger.error(f"Error configuring S3 trigger: {str(e)}")
        raise


if __name__ == "__main__":
    logger.info("Starting deployment...")

    lambda_role = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/{LAMBDA_ROLE_NAME}"
    sf_role = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/{SF_ROLE_NAME}"

    # Create or update all Lambda functions
    lambdas = {
        "TaskOne": create_lambda_function(
            LAMBDA_FUNCTION_ONE,
            f"{LAMBDA_FOLDER}/task_one.zip",
            lambda_role,
            "app_task_one.lambda_handler",
        ),
        "TaskTwo": create_lambda_function(
            LAMBDA_FUNCTION_TWO, f"{LAMBDA_FOLDER}/task_two.zip", lambda_role, "app_task_two.lambda_handler"
        ),
        "S3Trigger": create_lambda_function(
            LAMBDA_FUNCTION_S3_TRIGGER, f"{LAMBDA_FOLDER}/s3_trigger.zip", lambda_role, "app_s3_trigger.lambda_handler"
        ),
    }

    deploy_state_machine("state_machine_definition.json", sf_role, lambdas)
    add_s3_trigger_to_bucket(S3_BUCKET_NAME, lambdas["S3Trigger"])

    logger.info("Deployment complete!")