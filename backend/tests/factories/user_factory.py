"""Factory for generating User test data."""

from uuid import uuid4

import factory

from src.models.user import User, UserTier


class UserFactory(factory.Factory):
    """Factory for creating User instances for testing.

    Usage:
        # Create a free user
        user = UserFactory()

        # Create a Pro user
        pro_user = UserFactory(tier=UserTier.PRO)

        # Create with specific email
        user = UserFactory(email="specific@example.com")
    """

    class Meta:
        model = User

    id = factory.LazyFunction(uuid4)
    google_id = factory.LazyFunction(lambda: f"google-{uuid4()}")
    email = factory.LazyFunction(lambda: f"user-{uuid4()}@example.com")
    name = factory.Faker("name")
    avatar_url = factory.Faker("image_url")
    timezone = "UTC"
    tier = UserTier.FREE

    class Params:
        """Factory parameters for creating different user variants."""

        pro = factory.Trait(tier=UserTier.PRO)
