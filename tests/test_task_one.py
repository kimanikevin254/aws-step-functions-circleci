import pytest

from aws_lambdas.task_one.app_task_one import lambda_handler


def test_lambda_handler_success() -> None:
    # Arrange
    test_event = {"document_id": "test123", "s3_path": "s3://test-bucket/folder/document.pdf"}

    # Act
    result = lambda_handler(test_event, None)

    # Assert
    assert result["bucket_name"] == "test-bucket"
    assert result["file_name"] == "document"
    assert result["file_extension"] == ".pdf"
    assert result["s3_path"] == "test-bucket/folder/document.pdf"


def test_lambda_handler_missing_s3_path() -> None:
    # Arrange
    test_event = {"document_id": "test123"}

    # Act & Assert
    with pytest.raises(KeyError):
        lambda_handler(test_event, None)