from typing import Any

from loguru import logger


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    try:
        document_id = event.get("document_id")
        file_extension = event.get("file_extension", "").lower()

        # Classify based on file extension
        if file_extension == ".pdf":
            doc_type = "PDF Document"
        elif file_extension == ".doc" or file_extension == ".docx":
            doc_type = "Word Document"
        elif file_extension == ".png" or file_extension == ".jpg" or file_extension == ".jpeg":
            doc_type = "Image File"
        else:
            doc_type = "Unknown Type"

        result = {
            "document_id": document_id,
            "classification": doc_type,
        }

        logger.info(f"Document {document_id} classified as: {doc_type}")
        return result

    except Exception as e:
        logger.error(f"Error in classification: {e}")
        raise