#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -eu

# Load environment variables from .env file
set -o allexport
source .env
set +o allexport

STATE_MACHINE_ARN=arn:aws:states:${AWS_REGION}:${AWS_ACCOUNT_ID}:stateMachine:${STATE_MACHINE_NAME}

# Create Lambda Execution Role
if aws iam get-role --role-name $LAMBDA_ROLE_NAME 2>/dev/null; then
  echo "✅ Lambda Role '$LAMBDA_ROLE_NAME' already exists."
else
  echo "🚀 Creating Lambda Role '$LAMBDA_ROLE_NAME'..."
  aws iam create-role --role-name $LAMBDA_ROLE_NAME \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Principal": { "Service": "lambda.amazonaws.com" },
        "Action": "sts:AssumeRole"
      }]
    }'

  # Attach the AWSLambdaBasicExecutionRole policy
  echo "🚀 Attaching AWSLambdaBasicExecutionRole policy to Lambda Role '$LAMBDA_ROLE_NAME'..."
  aws iam attach-role-policy --role-name $LAMBDA_ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

  # Attach the custom policy to allow starting Step Functions executions
  echo "🚀 Attaching custom policy to Lambda Role '$LAMBDA_ROLE_NAME'..."
  aws iam put-role-policy --role-name $LAMBDA_ROLE_NAME \
    --policy-name LambdaStartStepFunctionPolicy \
    --policy-document "{
      \"Version\": \"2012-10-17\",
      \"Statement\": [{
        \"Effect\": \"Allow\",
        \"Action\": \"states:StartExecution\",
        \"Resource\": \"${STATE_MACHINE_ARN}\"
      }]
    }"

fi


# Create Step Functions Execution Role
if aws iam get-role --role-name $SF_ROLE_NAME 2>/dev/null; then
  echo "✅ Step Function Role '$SF_ROLE_NAME' already exists."
else
  # Create the step function role
  echo "🚀 Creating Step Function Role '$SF_ROLE_NAME'..."
  aws iam create-role --role-name $SF_ROLE_NAME \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Principal": { "Service": "states.amazonaws.com" },
        "Action": "sts:AssumeRole"
      }]
    }'

  # Attach the custom policy to allow invoking Lambda functions
  echo "🚀 Attaching custom policy to Step Function Role '$SF_ROLE_NAME'..."
  aws iam put-role-policy --role-name $SF_ROLE_NAME \
    --policy-name StepFunctionLambdaInvokePolicy \
    --policy-document '{
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Action": "lambda:InvokeFunction",
        "Resource": "*"
      }]
    }'
fi

echo "🎯 All roles are ready!"