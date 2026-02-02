"""Deepgram client for voice transcription.

Phase 13: Voice Transcription (Priority: P3)

T267: Implement DeepgramClient with NOVA2 model per research.md Section 6
- Uses Deepgram NOVA2 model for best accuracy
- Handles timeouts and connection errors gracefully
- Supports retry for transient errors
"""

import asyncio
from typing import Any

import httpx

from src.config import Settings
from src.schemas.ai_agents import TranscriptionResult


# =============================================================================
# EXCEPTIONS
# =============================================================================


class DeepgramError(Exception):
    """Base exception for Deepgram errors."""

    pass


class DeepgramTimeoutError(DeepgramError):
    """Raised when Deepgram API times out."""

    pass


class DeepgramConnectionError(DeepgramError):
    """Raised when connection to Deepgram fails."""

    pass


class DeepgramAPIError(DeepgramError):
    """Raised when Deepgram returns an error response."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


# =============================================================================
# DEEPGRAM CLIENT
# =============================================================================


class DeepgramClient:
    """Client for Deepgram voice transcription API.

    T267: Implements NOVA2 model transcription with:
    - Automatic retry for 5xx errors
    - Timeout handling
    - Structured result parsing

    Per research.md Section 6 - Deepgram NOVA2 for voice transcription.
    """

    # Deepgram API base URL
    BASE_URL = "https://api.deepgram.com/v1"

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 1.0

    # Retryable status codes (server errors)
    RETRYABLE_STATUS_CODES = {500, 502, 503, 504}

    def __init__(self, settings: Settings):
        """Initialize Deepgram client.

        Args:
            settings: Application settings with Deepgram API key
        """
        self.settings = settings
        self.api_key = settings.deepgram_api_key.get_secret_value()
        self.model = settings.deepgram_model
        self.timeout_seconds = settings.deepgram_timeout_seconds

        # Create async HTTP client
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout_seconds),
            headers={
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json",
            },
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def transcribe(
        self,
        audio_url: str,
        duration_seconds: int,
        language: str = "en",
    ) -> TranscriptionResult:
        """Transcribe audio from URL using Deepgram NOVA2.

        Args:
            audio_url: URL of the audio file to transcribe
            duration_seconds: Duration of the audio in seconds
            language: Language code (default: en)

        Returns:
            TranscriptionResult with text, confidence, and language

        Raises:
            DeepgramTimeoutError: If request times out
            DeepgramConnectionError: If connection fails
            DeepgramAPIError: If API returns an error
        """
        # Build request URL with query parameters
        params = {
            "model": self.model,
            "language": language,
            "smart_format": "true",
            "punctuate": "true",
            "diarize": "false",
        }

        url = f"{self.BASE_URL}/listen"
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        full_url = f"{url}?{query_string}"

        # Request body with audio URL
        body = {"url": audio_url}

        # Attempt with retries
        last_error: Exception | None = None

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self._client.post(full_url, json=body)

                # Check for retryable errors
                if response.status_code in self.RETRYABLE_STATUS_CODES:
                    last_error = DeepgramAPIError(
                        f"Deepgram API error: {response.status_code}",
                        status_code=response.status_code,
                    )
                    if attempt < self.MAX_RETRIES - 1:
                        await asyncio.sleep(
                            self.RETRY_DELAY_SECONDS * (attempt + 1)
                        )
                        continue
                    raise last_error

                # Raise for other non-2xx responses
                response.raise_for_status()

                # Parse successful response
                return self._parse_response(response.json())

            except httpx.TimeoutException as e:
                raise DeepgramTimeoutError(
                    f"Deepgram request timed out after {self.timeout_seconds}s"
                ) from e

            except httpx.ConnectError as e:
                raise DeepgramConnectionError(
                    f"Failed to connect to Deepgram API: {e}"
                ) from e

            except httpx.HTTPStatusError as e:
                raise DeepgramAPIError(
                    f"Deepgram API error: {e.response.status_code} - {e.response.text}",
                    status_code=e.response.status_code,
                ) from e

        # If we get here, all retries failed
        if last_error:
            raise last_error
        raise DeepgramAPIError("Unknown error during transcription")

    async def transcribe_bytes(
        self,
        audio_data: bytes,
        content_type: str = "audio/webm",
        language: str = "en",
    ) -> TranscriptionResult:
        """Transcribe audio from bytes using Deepgram NOVA2.

        Args:
            audio_data: Raw audio bytes
            content_type: MIME type of the audio (e.g., audio/webm)
            language: Language code (default: en)

        Returns:
            TranscriptionResult with text, confidence, and language

        Raises:
            DeepgramTimeoutError: If request times out
            DeepgramConnectionError: If connection fails
            DeepgramAPIError: If API returns an error
        """
        # Build request URL with query parameters
        params = {
            "model": self.model,
            "language": language,
            "smart_format": "true",
            "punctuate": "true",
        }

        url = f"{self.BASE_URL}/listen"
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        full_url = f"{url}?{query_string}"

        # Override content-type header for raw audio
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": content_type,
        }

        # Attempt with retries
        last_error: Exception | None = None

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self._client.post(
                    full_url,
                    content=audio_data,
                    headers=headers,
                )

                # Check for retryable errors
                if response.status_code in self.RETRYABLE_STATUS_CODES:
                    last_error = DeepgramAPIError(
                        f"Deepgram API error: {response.status_code}",
                        status_code=response.status_code,
                    )
                    if attempt < self.MAX_RETRIES - 1:
                        await asyncio.sleep(
                            self.RETRY_DELAY_SECONDS * (attempt + 1)
                        )
                        continue
                    raise last_error

                response.raise_for_status()
                return self._parse_response(response.json())

            except httpx.TimeoutException as e:
                raise DeepgramTimeoutError(
                    f"Deepgram request timed out after {self.timeout_seconds}s"
                ) from e

            except httpx.ConnectError as e:
                raise DeepgramConnectionError(
                    f"Failed to connect to Deepgram API: {e}"
                ) from e

            except httpx.HTTPStatusError as e:
                raise DeepgramAPIError(
                    f"Deepgram API error: {e.response.status_code}",
                    status_code=e.response.status_code,
                ) from e

        if last_error:
            raise last_error
        raise DeepgramAPIError("Unknown error during transcription")

    def _parse_response(self, data: dict[str, Any]) -> TranscriptionResult:
        """Parse Deepgram API response.

        Args:
            data: Raw JSON response from Deepgram

        Returns:
            Parsed TranscriptionResult
        """
        # Extract transcript from response
        results = data.get("results", {})
        channels = results.get("channels", [])

        if not channels:
            return TranscriptionResult(
                text="",
                language="en",
                confidence=0.0,
            )

        # Get first channel's first alternative
        alternatives = channels[0].get("alternatives", [])
        if not alternatives:
            return TranscriptionResult(
                text="",
                language="en",
                confidence=0.0,
            )

        alternative = alternatives[0]
        transcript = alternative.get("transcript", "")
        confidence = alternative.get("confidence", 0.0)

        # Get detected language from metadata
        metadata = data.get("metadata", {})
        language = metadata.get("detected_language", "en")

        # Get word-level timing if available
        words = alternative.get("words")

        # Get duration
        duration = metadata.get("duration")

        return TranscriptionResult(
            text=transcript,
            language=language,
            confidence=confidence,
            words=words,
            duration_seconds=duration,
        )


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def get_deepgram_client(settings: Settings) -> DeepgramClient:
    """Get a DeepgramClient instance."""
    return DeepgramClient(settings)
