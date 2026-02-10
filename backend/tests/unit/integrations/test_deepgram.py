"""Unit tests for Deepgram client.

Phase 13: Voice Transcription (Priority: P3)
Tests for FR-033, FR-036.

T266: Deepgram client handles timeout
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import httpx

from src.config import Settings


# =============================================================================
# TEST: T266 - Deepgram client handles timeout
# =============================================================================


@pytest.mark.asyncio
async def test_deepgram_client_handles_timeout(settings: Settings):
    """T266: Deepgram client handles timeout gracefully."""
    from src.integrations.deepgram_client import DeepgramClient, DeepgramTimeoutError

    client = DeepgramClient(settings=settings)

    # Mock httpx to raise timeout
    with patch.object(client, '_client') as mock_client:
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Connection timed out"))

        with pytest.raises(DeepgramTimeoutError) as exc_info:
            await client.transcribe(
                audio_url="https://storage.example.com/audio/test.webm",
                duration_seconds=30,
            )

        assert "timed out" in str(exc_info.value).lower() or "timeout" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_deepgram_client_handles_connection_error(settings: Settings):
    """T266 (edge): Deepgram client handles connection errors."""
    from src.integrations.deepgram_client import DeepgramClient, DeepgramConnectionError

    client = DeepgramClient(settings=settings)

    # Mock httpx to raise connection error
    with patch.object(client, '_client') as mock_client:
        mock_client.post = AsyncMock(
            side_effect=httpx.ConnectError("Failed to connect to Deepgram API")
        )

        with pytest.raises(DeepgramConnectionError) as exc_info:
            await client.transcribe(
                audio_url="https://storage.example.com/audio/test.webm",
                duration_seconds=30,
            )

        assert "connect" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_deepgram_client_handles_api_error(settings: Settings):
    """T266 (edge): Deepgram client handles API errors (non-2xx responses)."""
    from src.integrations.deepgram_client import DeepgramClient, DeepgramAPIError

    client = DeepgramClient(settings=settings)

    # Mock httpx to return error response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError(
            "Server error",
            request=MagicMock(),
            response=mock_response,
        )
    )

    with patch.object(client, '_client') as mock_client:
        mock_client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(DeepgramAPIError) as exc_info:
            await client.transcribe(
                audio_url="https://storage.example.com/audio/test.webm",
                duration_seconds=30,
            )

        assert "500" in str(exc_info.value) or "error" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_deepgram_client_successful_transcription(settings: Settings):
    """T266 (positive): Deepgram client returns transcription on success."""
    from src.integrations.deepgram_client import DeepgramClient
    from src.schemas.ai_agents import TranscriptionResult

    client = DeepgramClient(settings=settings)

    # Mock successful Deepgram response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": {
            "channels": [
                {
                    "alternatives": [
                        {
                            "transcript": "This is a test transcription from Deepgram",
                            "confidence": 0.95,
                        }
                    ]
                }
            ]
        },
        "metadata": {
            "detected_language": "en",
        },
    }
    mock_response.raise_for_status = MagicMock()

    with patch.object(client, '_client') as mock_client:
        mock_client.post = AsyncMock(return_value=mock_response)

        result = await client.transcribe(
            audio_url="https://storage.example.com/audio/test.webm",
            duration_seconds=30,
        )

    assert isinstance(result, TranscriptionResult)
    assert result.text == "This is a test transcription from Deepgram"
    assert result.language == "en"
    assert result.confidence == 0.95


@pytest.mark.asyncio
async def test_deepgram_client_uses_nova2_model(settings: Settings):
    """T266 (spec): Deepgram client uses NOVA2 model as specified."""
    from src.integrations.deepgram_client import DeepgramClient

    client = DeepgramClient(settings=settings)

    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": {
            "channels": [{"alternatives": [{"transcript": "test", "confidence": 0.9}]}]
        },
        "metadata": {"detected_language": "en"},
    }
    mock_response.raise_for_status = MagicMock()

    captured_url = None

    async def capture_request(*args, **kwargs):
        nonlocal captured_url
        captured_url = args[0] if args else kwargs.get("url")
        return mock_response

    with patch.object(client, '_client') as mock_client:
        mock_client.post = AsyncMock(side_effect=capture_request)

        await client.transcribe(
            audio_url="https://storage.example.com/audio/test.webm",
            duration_seconds=30,
        )

    # Verify NOVA2 model is specified in the request
    assert captured_url is not None
    assert "model=nova-2" in captured_url or client.model == "nova-2"


@pytest.mark.asyncio
async def test_deepgram_client_retries_on_transient_error(settings: Settings):
    """T266 (resilience): Deepgram client retries on transient errors."""
    from src.integrations.deepgram_client import DeepgramClient
    from src.schemas.ai_agents import TranscriptionResult

    client = DeepgramClient(settings=settings)

    # First call fails, second succeeds
    mock_error_response = MagicMock()
    mock_error_response.status_code = 503
    mock_error_response.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError(
            "Service unavailable", request=MagicMock(), response=mock_error_response
        )
    )

    mock_success_response = MagicMock()
    mock_success_response.status_code = 200
    mock_success_response.json.return_value = {
        "results": {
            "channels": [{"alternatives": [{"transcript": "success", "confidence": 0.9}]}]
        },
        "metadata": {"detected_language": "en"},
    }
    mock_success_response.raise_for_status = MagicMock()

    call_count = 0

    async def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_error_response
        return mock_success_response

    with patch.object(client, '_client') as mock_client:
        mock_client.post = AsyncMock(side_effect=mock_post)

        result = await client.transcribe(
            audio_url="https://storage.example.com/audio/test.webm",
            duration_seconds=30,
        )

    # Verify retry happened
    assert call_count >= 2
    assert result.text == "success"


@pytest.mark.asyncio
async def test_deepgram_client_respects_timeout_setting(settings: Settings):
    """T266 (spec): Deepgram client respects configured timeout."""
    from src.integrations.deepgram_client import DeepgramClient

    # Override timeout in settings
    settings.deepgram_timeout_seconds = 30

    client = DeepgramClient(settings=settings)

    # Verify timeout is configured correctly
    assert client.timeout_seconds == 30
