"""Unit tests for AuthService.

T062-T066: Auth service tests per api-specification.md Section 2
TDD RED Phase: These tests should FAIL until AuthService is implemented.
"""

from datetime import datetime, timedelta, UTC
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.auth import RefreshToken
from src.models.user import User
from src.schemas.enums import UserTier


# =============================================================================
# T062: Google OAuth callback creates new user
# =============================================================================


@pytest.mark.asyncio
async def test_google_oauth_callback_creates_new_user(
    db_session: AsyncSession,
    settings: Settings,
):
    """T062: Google OAuth callback creates new user.

    Given: A valid Google ID token for a user not in the database
    When: AuthService.create_or_update_user is called
    Then: A new user is created with correct profile data
    """
    from src.services.auth_service import AuthService

    auth_service = AuthService(db_session, settings)

    # Mock Google token data
    google_user_data = {
        "sub": "google-id-123456789",
        "email": "newuser@example.com",
        "name": "New User",
        "picture": "https://lh3.googleusercontent.com/avatar.jpg",
    }

    user = await auth_service.create_or_update_user(google_user_data)

    assert user is not None
    assert user.google_id == google_user_data["sub"]
    assert user.email == google_user_data["email"]
    assert user.name == google_user_data["name"]
    assert user.avatar_url == google_user_data["picture"]
    assert user.tier == UserTier.FREE  # New users start as free


# =============================================================================
# T063: Google OAuth callback returns existing user
# =============================================================================


@pytest.mark.asyncio
async def test_google_oauth_callback_returns_existing_user(
    db_session: AsyncSession,
    settings: Settings,
    test_user: User,
):
    """T063: Google OAuth callback returns existing user.

    Given: A valid Google ID token for a user already in the database
    When: AuthService.create_or_update_user is called
    Then: The existing user is returned (not duplicated)
    """
    from src.services.auth_service import AuthService

    auth_service = AuthService(db_session, settings)

    # Use the existing test user's Google ID
    google_user_data = {
        "sub": test_user.google_id,
        "email": test_user.email,
        "name": "Updated Name",  # Name might be updated from Google
        "picture": "https://lh3.googleusercontent.com/new-avatar.jpg",
    }

    user = await auth_service.create_or_update_user(google_user_data)

    assert user is not None
    assert user.id == test_user.id  # Same user, not a new one
    assert user.google_id == test_user.google_id
    # Profile may be updated
    assert user.name == "Updated Name"


# =============================================================================
# T064: Access token JWT contains correct claims
# =============================================================================


@pytest.mark.asyncio
async def test_access_token_contains_correct_claims(
    db_session: AsyncSession,
    settings: Settings,
    test_user: User,
):
    """T064: Access token JWT contains correct claims (sub, email, tier).

    Given: A valid user
    When: AuthService.generate_tokens is called
    Then: Access token contains sub (user ID), email, tier claims
    """
    from src.services.auth_service import AuthService
    from src.dependencies import JWTKeyManager

    auth_service = AuthService(db_session, settings)
    jwt_manager = JWTKeyManager(settings)

    access_token, refresh_token = await auth_service.generate_tokens(test_user)

    assert access_token is not None
    assert refresh_token is not None

    # Decode and verify claims
    payload = jwt_manager.decode_token(access_token, token_type="access")

    assert payload["sub"] == str(test_user.id)
    assert payload["email"] == test_user.email
    assert payload["tier"] == test_user.tier.value
    assert payload["iss"] == "perpetua-flow"
    assert "exp" in payload
    assert "iat" in payload


# =============================================================================
# T065: Refresh token rotation issues new tokens
# =============================================================================


@pytest.mark.asyncio
async def test_refresh_token_rotation_issues_new_tokens(
    db_session: AsyncSession,
    settings: Settings,
    test_user: User,
):
    """T065: Refresh token rotation issues new tokens.

    Given: A valid refresh token
    When: AuthService.refresh_tokens is called
    Then: New access and refresh tokens are issued, old refresh token is revoked
    """
    from src.services.auth_service import AuthService

    auth_service = AuthService(db_session, settings)

    # Generate initial tokens
    access_token_1, refresh_token_1 = await auth_service.generate_tokens(test_user)

    # Refresh tokens
    access_token_2, refresh_token_2 = await auth_service.refresh_tokens(refresh_token_1)

    # New tokens should be issued
    assert access_token_2 is not None
    assert refresh_token_2 is not None
    assert access_token_2 != access_token_1
    assert refresh_token_2 != refresh_token_1

    # Old refresh token should be invalid/revoked (cannot be used again)
    with pytest.raises(Exception):  # Should raise InvalidTokenError or similar
        await auth_service.refresh_tokens(refresh_token_1)


# =============================================================================
# T066: Invalid refresh token returns error
# =============================================================================


@pytest.mark.asyncio
async def test_invalid_refresh_token_raises_error(
    db_session: AsyncSession,
    settings: Settings,
):
    """T066: Invalid refresh token returns 401.

    Given: An invalid or expired refresh token
    When: AuthService.refresh_tokens is called
    Then: An authentication error is raised
    """
    from src.services.auth_service import AuthService, InvalidRefreshTokenError

    auth_service = AuthService(db_session, settings)

    invalid_token = "invalid.refresh.token"

    with pytest.raises(InvalidRefreshTokenError):
        await auth_service.refresh_tokens(invalid_token)


@pytest.mark.asyncio
async def test_expired_refresh_token_raises_error(
    db_session: AsyncSession,
    settings: Settings,
    test_user: User,
):
    """T066: Expired refresh token returns 401.

    Given: An expired refresh token
    When: AuthService.refresh_tokens is called
    Then: An authentication error is raised
    """
    import hashlib
    from src.services.auth_service import AuthService, InvalidRefreshTokenError

    auth_service = AuthService(db_session, settings)

    # Create an expired refresh token in the database
    expired_token = "expired-refresh-token-12345"
    token_hash = hashlib.sha256(expired_token.encode()).hexdigest()

    db_refresh_token = RefreshToken(
        id=uuid4(),
        user_id=test_user.id,
        token_hash=token_hash,
        expires_at=datetime.now(UTC) - timedelta(days=1),  # Expired
        revoked=False,
    )
    db_session.add(db_refresh_token)
    await db_session.commit()

    with pytest.raises(InvalidRefreshTokenError):
        await auth_service.refresh_tokens(expired_token)


@pytest.mark.asyncio
async def test_revoked_refresh_token_raises_error(
    db_session: AsyncSession,
    settings: Settings,
    test_user: User,
):
    """T066: Revoked refresh token returns 401.

    Given: A revoked refresh token
    When: AuthService.refresh_tokens is called
    Then: An authentication error is raised
    """
    import hashlib
    from src.services.auth_service import AuthService, InvalidRefreshTokenError

    auth_service = AuthService(db_session, settings)

    # Create a revoked refresh token in the database
    revoked_token = "revoked-refresh-token-12345"
    token_hash = hashlib.sha256(revoked_token.encode()).hexdigest()

    db_refresh_token = RefreshToken(
        id=uuid4(),
        user_id=test_user.id,
        token_hash=token_hash,
        expires_at=datetime.now(UTC) + timedelta(days=7),
        revoked=True,
        revoked_at=datetime.now(UTC),
    )
    db_session.add(db_refresh_token)
    await db_session.commit()

    with pytest.raises(InvalidRefreshTokenError):
        await auth_service.refresh_tokens(revoked_token)


# =============================================================================
# T078c: User profile update validates timezone and name
# =============================================================================


@pytest.mark.asyncio
async def test_user_profile_update_validates_timezone(
    db_session: AsyncSession,
    settings: Settings,
    test_user: User,
):
    """T078c: User profile update validates timezone.

    Given: An update request with an invalid timezone
    When: UserService.update_profile is called
    Then: A validation error is raised
    """
    from src.services.user_service import UserService, InvalidTimezoneError

    user_service = UserService(db_session, settings)

    with pytest.raises(InvalidTimezoneError):
        await user_service.update_profile(
            user=test_user,
            name=None,
            timezone="Invalid/Timezone",
        )


@pytest.mark.asyncio
async def test_user_profile_update_validates_name_length(
    db_session: AsyncSession,
    settings: Settings,
    test_user: User,
):
    """T078c: User profile update validates name length.

    Given: An update request with a name exceeding 100 characters
    When: UserService.update_profile is called
    Then: A validation error is raised
    """
    from src.services.user_service import UserService, InvalidNameError

    user_service = UserService(db_session, settings)

    long_name = "A" * 101  # Exceeds 100 char limit

    with pytest.raises(InvalidNameError):
        await user_service.update_profile(
            user=test_user,
            name=long_name,
            timezone=None,
        )


@pytest.mark.asyncio
async def test_user_profile_update_succeeds_with_valid_data(
    db_session: AsyncSession,
    settings: Settings,
    test_user: User,
):
    """T078c: User profile update succeeds with valid data.

    Given: An update request with valid timezone and name
    When: UserService.update_profile is called
    Then: The user profile is updated successfully
    """
    from src.services.user_service import UserService

    user_service = UserService(db_session, settings)

    updated_user = await user_service.update_profile(
        user=test_user,
        name="Updated Name",
        timezone="America/New_York",
    )

    assert updated_user.name == "Updated Name"
    assert updated_user.timezone == "America/New_York"
