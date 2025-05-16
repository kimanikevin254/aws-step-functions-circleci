from aws_lambdas.task_two.app_task_two import lambda_handler


def test_lambda_handler_pdf() -> None:
    # Arrange
    test_event = {"document_id": "test123", "file_extension": ".pdf"}

    # Act
    result = lambda_handler(test_event, None)

    # Assert
    assert result["document_id"] == "test123"
    assert result["classification"] == "PDF Document"


def test_lambda_handler_image() -> None:
    # Arrange
    test_event = {"document_id": "test123", "file_extension": ".jpg"}

    # Act
    result = lambda_handler(test_event, None)

    # Assert
    assert result["document_id"] == "test123"
    assert result["classification"] == "Image File"


def test_lambda_handler_unknown() -> None:
    # Arrange
    test_event = {"document_id": "test123", "file_extension": ".xyz"}

    # Act
    result = lambda_handler(test_event, None)

    # Assert
    assert result["document_id"] == "test123"
    assert result["classification"] == "Unknown Type"