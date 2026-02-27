from opencore.interface.middleware import global_exception_handler, ErrorResponse
from fastapi import HTTPException, Request
from unittest.mock import MagicMock
import pytest
import asyncio

@pytest.mark.asyncio
async def test_global_exception_handler_http_exception():
    # Create a mock request
    mock_request = MagicMock(spec=Request)
    mock_request.method = "GET"
    mock_request.url.path = "/test"

    # Create an HTTPException
    exc = HTTPException(status_code=404, detail="Resource not found")

    # Call the handler
    response = await global_exception_handler(mock_request, exc)

    # Decode response body
    import json
    body = json.loads(response.body)

    # Check structure
    assert "error" in body
    assert body["error"]["code"] == "HTTP_404"
    assert body["error"]["message"] == "Resource not found"
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_global_exception_handler_generic_exception():
    # Create a mock request
    mock_request = MagicMock(spec=Request)
    mock_request.method = "GET"
    mock_request.url.path = "/test"

    # Create a generic Exception
    exc = Exception("Something went wrong")

    # Call the handler
    response = await global_exception_handler(mock_request, exc)

    # Decode response body
    import json
    body = json.loads(response.body)

    # Check structure
    assert "error" in body
    assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert body["error"]["message"] == "An unexpected error occurred."
    assert response.status_code == 500
