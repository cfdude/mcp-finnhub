"""Unit tests for Finnhub API error handling."""

from __future__ import annotations

import httpx

from mcp_finnhub.api.errors import (
    AuthenticationError,
    FinnhubAPIError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    ValidationError,
    handle_api_error,
)


class TestFinnhubAPIError:
    """Tests for base FinnhubAPIError class."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = FinnhubAPIError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.status_code is None
        assert error.response_data == {}
        assert error.request_url is None
        assert error.request_params == {}

    def test_error_with_context(self):
        """Test error with full context."""
        error = FinnhubAPIError(
            "Test error",
            status_code=500,
            response_data={"error": "Server error"},
            request_url="https://finnhub.io/api/v1/quote",
            request_params={"symbol": "AAPL"},
        )
        assert error.status_code == 500
        assert error.response_data == {"error": "Server error"}
        assert error.request_url == "https://finnhub.io/api/v1/quote"
        assert error.request_params == {"symbol": "AAPL"}

    def test_error_string_formatting(self):
        """Test error string representation."""
        error = FinnhubAPIError(
            "Test error",
            status_code=404,
            request_url="https://finnhub.io/api/v1/quote",
            request_params={"symbol": "INVALID"},
        )
        error_str = str(error)
        assert "Test error" in error_str
        assert "404" in error_str
        assert "/quote" in error_str
        assert "symbol=INVALID" in error_str


class TestSpecificErrors:
    """Tests for specific error subclasses."""

    def test_authentication_error(self):
        """Test AuthenticationError defaults."""
        error = AuthenticationError()
        assert error.status_code == 401
        assert "API key" in error.message

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError("Custom auth error")
        assert error.status_code == 401
        assert error.message == "Custom auth error"

    def test_permission_error(self):
        """Test PermissionError defaults."""
        error = PermissionError()
        assert error.status_code == 403
        assert "permission" in error.message.lower()

    def test_not_found_error(self):
        """Test NotFoundError defaults."""
        error = NotFoundError()
        assert error.status_code == 404
        assert "not found" in error.message.lower()

    def test_rate_limit_error(self):
        """Test RateLimitError defaults."""
        error = RateLimitError()
        assert error.status_code == 429
        assert "rate limit" in error.message.lower()

    def test_server_error(self):
        """Test ServerError defaults."""
        error = ServerError()
        assert "server error" in error.message.lower()

    def test_validation_error(self):
        """Test ValidationError defaults."""
        error = ValidationError()
        assert error.status_code == 400
        assert "invalid" in error.message.lower()


class TestHandleApiError:
    """Tests for handle_api_error function."""

    def test_handle_401_error(self):
        """Test handling 401 authentication error."""
        response = httpx.Response(
            401,
            json={"error": "Invalid API key"},
            request=httpx.Request("GET", "https://finnhub.io/api/v1/quote?symbol=AAPL"),
        )
        error = handle_api_error(response)
        assert isinstance(error, AuthenticationError)
        assert error.status_code == 401
        assert "Invalid API key" in error.message
        assert error.request_url == "https://finnhub.io/api/v1/quote?symbol=AAPL"
        assert error.request_params == {"symbol": "AAPL"}

    def test_handle_403_error(self):
        """Test handling 403 permission error."""
        response = httpx.Response(
            403,
            json={"error": "Premium endpoint"},
            request=httpx.Request("GET", "https://finnhub.io/api/v1/premium"),
        )
        error = handle_api_error(response)
        assert isinstance(error, PermissionError)
        assert error.status_code == 403

    def test_handle_404_error(self):
        """Test handling 404 not found error."""
        response = httpx.Response(
            404,
            json={"error": "Symbol not found"},
            request=httpx.Request("GET", "https://finnhub.io/api/v1/quote?symbol=INVALID"),
        )
        error = handle_api_error(response)
        assert isinstance(error, NotFoundError)
        assert error.status_code == 404

    def test_handle_429_error(self):
        """Test handling 429 rate limit error."""
        response = httpx.Response(
            429,
            json={"error": "Rate limit exceeded"},
            request=httpx.Request("GET", "https://finnhub.io/api/v1/quote"),
        )
        error = handle_api_error(response)
        assert isinstance(error, RateLimitError)
        assert error.status_code == 429

    def test_handle_400_error(self):
        """Test handling 400 validation error."""
        response = httpx.Response(
            400,
            json={"error": "Missing required parameter"},
            request=httpx.Request("GET", "https://finnhub.io/api/v1/quote"),
        )
        error = handle_api_error(response)
        assert isinstance(error, ValidationError)
        assert error.status_code == 400

    def test_handle_500_error(self):
        """Test handling 500 server error."""
        response = httpx.Response(
            500,
            json={"error": "Internal server error"},
            request=httpx.Request("GET", "https://finnhub.io/api/v1/quote"),
        )
        error = handle_api_error(response)
        assert isinstance(error, ServerError)
        assert error.status_code == 500

    def test_handle_502_error(self):
        """Test handling 502 bad gateway error."""
        response = httpx.Response(
            502,
            text="Bad Gateway",
            request=httpx.Request("GET", "https://finnhub.io/api/v1/quote"),
        )
        error = handle_api_error(response)
        assert isinstance(error, ServerError)
        assert error.status_code == 502

    def test_handle_non_json_response(self):
        """Test handling response with non-JSON body."""
        response = httpx.Response(
            500,
            text="Internal Server Error",
            request=httpx.Request("GET", "https://finnhub.io/api/v1/quote"),
        )
        error = handle_api_error(response)
        assert isinstance(error, ServerError)
        assert "Internal Server Error" in error.message

    def test_handle_empty_response(self):
        """Test handling response with empty body."""
        response = httpx.Response(
            500,
            text="",
            request=httpx.Request("GET", "https://finnhub.io/api/v1/quote"),
        )
        error = handle_api_error(response)
        assert isinstance(error, ServerError)
        assert error.status_code == 500

    def test_handle_message_field(self):
        """Test extracting error from 'message' field."""
        response = httpx.Response(
            400,
            json={"message": "Invalid parameter"},
            request=httpx.Request("GET", "https://finnhub.io/api/v1/quote"),
        )
        error = handle_api_error(response)
        assert "Invalid parameter" in error.message

    def test_handle_unexpected_status_code(self):
        """Test handling unexpected status code."""
        response = httpx.Response(
            418,  # I'm a teapot
            json={"error": "Unusual error"},
            request=httpx.Request("GET", "https://finnhub.io/api/v1/quote"),
        )
        error = handle_api_error(response)
        assert isinstance(error, FinnhubAPIError)
        assert error.status_code == 418


class TestErrorIntegration:
    """Integration tests for error handling with httpx."""

    def test_error_from_http_status_error(self):
        """Test converting httpx.HTTPStatusError to FinnhubAPIError."""
        response = httpx.Response(
            404,
            json={"error": "Not found"},
            request=httpx.Request("GET", "https://finnhub.io/api/v1/quote?symbol=INVALID"),
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            error = handle_api_error(exc.response)
            assert isinstance(error, NotFoundError)
            assert error.status_code == 404
            assert error.request_params == {"symbol": "INVALID"}
