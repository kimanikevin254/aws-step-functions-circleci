#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -eu

# Store the root directory path
ROOT_DIR=$(pwd)

# Load environment variables from .env file
set -o allexport
source .env
set +o allexport

echo "✅ Environment variables loaded."

# Create dist folder if it doesn't exist
mkdir -p "${ROOT_DIR}/${LAMBDA_FOLDER}"
echo "✅ Created ${LAMBDA_FOLDER} directory"

# Function to zip Lambda with dependencies
zip_lambda_with_deps() {
    LAMBDA_NAME=$1
    ZIP_FILE="${ROOT_DIR}/${LAMBDA_FOLDER}/${LAMBDA_NAME}.zip"
    REQUIREMENTS_FILE="${ROOT_DIR}/requirements.txt"

    echo "📦 Processing ${LAMBDA_NAME}..."

    # Create package directory if it doesn't exist
    PACKAGE_DIR="${ROOT_DIR}/aws_lambdas/${LAMBDA_NAME}/package"
    mkdir -p "${PACKAGE_DIR}"

    # Install dependencies
    cd "${ROOT_DIR}/aws_lambdas/${LAMBDA_NAME}"
    pip install --target ./package -r "${REQUIREMENTS_FILE}" --upgrade --no-cache-dir

    # Create the zip file
    cd package
    zip -r9 "${ZIP_FILE}" .
    cd ..
    zip -g "${ZIP_FILE}" ./*.py

    # Clean up package directory
    rm -rf "${PACKAGE_DIR}"

    # Return to root directory
    cd "${ROOT_DIR}"
}

echo "🚀 Zipping Lambda functions..."

# Zip task_one
echo "📦 Zipping task_one..."
zip_lambda_with_deps "task_one"

# Zip task_two
echo "📦 Zipping task_two..."
zip_lambda_with_deps "task_two"

# Zip s3_trigger
echo "📦 Zipping s3_trigger..."
zip_lambda_with_deps "s3_trigger"

echo "✅ Lambda functions zipped successfully: ${LAMBDA_FOLDER}/task_one.zip, ${LAMBDA_FOLDER}/task_two.zip, ${LAMBDA_FOLDER}/s3_trigger.zip"