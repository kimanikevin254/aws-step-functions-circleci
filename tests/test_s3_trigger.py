from typing import Any

import pytest

from aws_lambdas.s3_trigger.app_s3_trigger import lambda_handler


@pytest.fixture
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STATE_MACHINE_NAME", "TestStateMachine")


def test_lambda_handler_success(mock_env_vars: None) -> None:
    # Arrange
    test_event = {"Records": [{"s3": {"bucket": {"name": "test-bucket"}, "object": {"key": "folder/document.pdf"}}}]}

    # Act
    result = lambda_handler(test_event, None)

    # Assert
    assert result["statusCode"] == 200
    assert "Step Functions execution started successfully" in result["body"]


def test_lambda_handler_invalid_event() -> None:
    # Arrange
    test_event: dict[str, Any] = {}

    # Act & Assert
    with pytest.raises(KeyError):
        lambda_handler(test_event, None)