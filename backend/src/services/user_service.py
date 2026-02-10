"""User service for profile management.

T078a-c: User profile endpoints per api-specification.md Section 3
"""

import logging
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings
from src.models.user import User


logger = logging.getLogger(__name__)


class UserServiceError(Exception):
    """Base exception for user service errors."""

    pass


class InvalidTimezoneError(UserServiceError):
    """Raised when an invalid timezone is provided."""

    pass


class InvalidNameError(UserServiceError):
    """Raised when an invalid name is provided."""

    pass


class UserService:
    """Service for user profile operations.

    Handles:
    - Profile retrieval
    - Profile updates (name, timezone)
    - Timezone validation
    """

    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings

    async def get_profile(self, user: User) -> User:
        """Get user profile.

        Args:
            user: The authenticated user

        Returns:
            The user with current profile data
        """
        await self.session.refresh(user)
        return user

    async def update_profile(
        self,
        user: User,
        name: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> User:
        """Update user profile.

        T078b: PATCH /api/v1/users/me per api-specification.md Section 3.2
        T078c: Validates timezone and name

        Args:
            user: The user to update
            name: New display name (1-100 chars, optional)
            timezone: New timezone (IANA format, optional)

        Returns:
            Updated user

        Raises:
            InvalidNameError: If name is invalid
            InvalidTimezoneError: If timezone is invalid
        """
        updated = False

        if name is not None:
            # Validate name length
            if len(name) < 1:
                raise InvalidNameError("Name must be at least 1 character")
            if len(name) > 100:
                raise InvalidNameError("Name must be at most 100 characters")

            user.name = name
            updated = True

        if timezone is not None:
            # Validate timezone using zoneinfo
            if not self._is_valid_timezone(timezone):
                raise InvalidTimezoneError(f"Invalid timezone: {timezone}")

            user.timezone = timezone
            updated = True

        if updated:
            self.session.add(user)
            await self.session.flush()
            await self.session.refresh(user)

        return user

    def _is_valid_timezone(self, timezone: str) -> bool:
        """Check if a timezone string is valid IANA timezone.

        Args:
            timezone: Timezone string to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            ZoneInfo(timezone)
            return True
        except ZoneInfoNotFoundError:
            return False
        except Exception:
            return False


def get_user_service(
    session: AsyncSession, settings: Settings
) -> UserService:
    """Get a UserService instance."""
    return UserService(session, settings)
