# AWS Step Functions with CircleCI

This project demonstrates how to deploy and manage Python-based AWS Step Functions using CircleCI, with Lambda functions handling two processing stages.

## Project Structure

```text
├── aws_lambdas/                      # Lambda function implementations
│   ├── __init__.py                   # Package initialization
│   ├── s3_trigger/                   # S3 event trigger Lambda
│   │   ├── __init__.py               # Package initialization
│   │   └── app_s3_trigger.py         # S3 trigger implementation
│   ├── task_one/                     # First processing task Lambda
│   │   ├── __init__.py               # Package initialization
│   │   └── app_task_one.py           # Task one implementation
│   └── task_two/                     # Second processing task Lambda
│       ├── __init__.py               # Package initialization
│       └── app_task_two.py           # Task two implementation
├── dist/                             # Distribution directory for Lambda packages
│   ├── s3_trigger.zip                # Packaged S3 trigger Lambda
│   ├── task_one.zip                  # Packaged task one Lambda
│   └── task_two.zip                  # Packaged task two Lambda
├── scripts/                          # Deployment and utility scripts
│   ├── create_roles.sh               # Script to create IAM roles
│   └── zip_lambdas.sh                # Script to zip Lambda functions
├── tests/                            # Test suite
│   ├── test_s3_trigger.py            # Test for S3 trigger Lambda
│   ├── test_task_one.py              # Test for Task One Lambda
│   └── test_task_two.py              # Test for Task Two Lambda
├── deploy.py                         # Main deployment script
├── LICENSE                           # Project license file
├── Makefile                          # Make commands for common tasks
├── pyproject.toml                    # Python project configuration
├── README.md                         # Project documentation
├── requirements.txt                  # Project dependencies for lambdas
├── state_machine_definition.json     # Step Functions state machine definition
└── uv.lock                           # UV package manager lock file
```

## Prerequisites

- Python 3.12
- AWS CLI configured with appropriate credentials
- UV package manager

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/benitomartin/aws-step-functions-circleci.git
   cd aws-step-functions-circleci
   ```

1. Install dependencies and activate virtual environment:

   ```bash
   uv sync --all-groups
   source .venv/bin/activate
   ```

1. Create and configure `.env` file based on `.env.example`:

   ```bash
   cp .env.example .env
   # Edit .env with your AWS configuration
   ```

1. Create an S3 bucket for document processing and update `.env`:

   ```bash
   aws s3api create-bucket \
      --bucket step-functions-$(uuidgen | tr -d - | tr '[:upper:]' '[:lower:]' ) \
      --region <your_aws_region> \
      --create-bucket-configuration LocationConstraint=<your_aws_region>
   ```

## Development

### Available Make Commands

- `make create-roles`: Create required IAM roles
- `make zip-lambdas`: Package Lambda functions
- `make deploy`: Deploy the Step Functions state machine
- `make test`: Run the test suite
- `make ruff`: Run Ruff linter
- `make mypy`: Run MyPy static type checker
- `make clean`: Clean up cached files

### Testing

Run the test suite:

```bash
make test
```

### Deployment

1. Create necessary IAM roles:

   ```bash
   make create-roles
   ```

1. Package Lambda functions:

   ```bash
   make zip-lambdas
   ```

1. Deploy the solution:

   ```bash
   make deploy
   ```

## Architecture

The solution consists of three Lambda functions:

1. **S3 Trigger** (`app_s3_trigger.py`):

   - Triggered by S3 file uploads
   - Initiates Step Functions execution

1. **Task One** (`app_task_one.py`):

   - Extracts metadata from uploaded files
   - Processes file information

1. **Task Two** (`app_task_two.py`):

   - Classifies documents based on file type
   - Handles different document formats

## Configuration

Main dependencies:

- `boto3`: AWS SDK for Python
- `loguru`: Logging utility
- `python-dotenv`: Environment variable management

Development dependencies:

- `mypy`: Static type checking
- `pytest`: Testing framework
- `ruff`: Python linter
- `pre-commit`: Git hooks for code quality

## License

See [LICENSE](LICENSE) file for details.
