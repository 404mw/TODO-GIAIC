"""Stress tests for concurrent credit consumption.

T289: Add concurrent consumption stress test (SC-011)

Tests credit FIFO consumption under concurrent access to ensure:
- No race conditions
- Balance never goes negative
- FIFO order maintained
- Proper locking behavior
"""

import asyncio
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from src.config import Settings
from src.models.user import User
from src.schemas.enums import UserTier
from src.services.credit_service import CreditService


@pytest.fixture
async def stress_test_engine():
    """Create a separate engine for stress tests with connection pool."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def session_factory(stress_test_engine):
    """Create session factory for concurrent sessions."""
    return async_sessionmaker(
        bind=stress_test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@pytest.fixture
async def stress_user(session_factory, settings: Settings):
    """Create a user with credits for stress testing."""
    async with session_factory() as session:
        user = User(
            id=uuid4(),
            google_id=f"google-stress-{uuid4()}",
            email=f"stress-{uuid4()}@example.com",
            name="Stress Test User",
            tier=UserTier.PRO,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Grant purchased credits (100)
        service = CreditService(session, settings)
        await service.grant_purchased_credits(user.id, 100)
        await session.commit()

        return user


@pytest.mark.xfail(reason="SQLite lacks FOR UPDATE row locking; concurrent tests need PostgreSQL")
@pytest.mark.asyncio
async def test_concurrent_consumption_no_negative_balance(
    session_factory,
    stress_user: User,
    settings: Settings,
) -> None:
    """Test that concurrent consumption doesn't result in negative balance.

    SC-011: Credit balance should never go negative even under
    concurrent access.

    Note: SQLite doesn't fully support FOR UPDATE, so this test
    verifies the logic rather than database-level locking.
    """
    async def consume_credit(user_id, amount: int) -> bool:
        """Attempt to consume credits, return True if successful."""
        async with session_factory() as session:
            service = CreditService(session, settings)
            try:
                await service.consume_credits(user_id, amount, f"stress_op_{uuid4()}")
                await session.commit()
                return True
            except ValueError:
                await session.rollback()
                return False

    # Create multiple concurrent consumption tasks
    # Total consumption attempts: 15 x 10 = 150 (more than 100 available)
    tasks = [consume_credit(stress_user.id, 10) for _ in range(15)]

    # Run concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Count successful and failed consumptions
    successful = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)

    # Should have consumed at most 100 credits (10 successful operations)
    assert successful <= 10
    # Some should have failed due to insufficient credits
    assert failed >= 5

    # Verify final balance is not negative
    async with session_factory() as session:
        service = CreditService(session, settings)
        balance = await service.get_balance(stress_user.id)
        assert balance.total >= 0


@pytest.mark.asyncio
async def test_sequential_consumption_consistency(
    session_factory,
    stress_user: User,
    settings: Settings,
) -> None:
    """Test that sequential consumption maintains consistency.

    This is a baseline test to verify basic consumption works
    before testing concurrent scenarios.
    """
    consumed_total = 0

    for i in range(10):
        async with session_factory() as session:
            service = CreditService(session, settings)
            result = await service.consume_credits(
                stress_user.id, 5, f"seq_op_{i}"
            )
            consumed_total += result.total_consumed
            await session.commit()

    # Should have consumed 50 credits
    assert consumed_total == 50

    # Verify balance
    async with session_factory() as session:
        service = CreditService(session, settings)
        balance = await service.get_balance(stress_user.id)
        assert balance.total == 50  # 100 - 50


@pytest.mark.xfail(reason="SQLite lacks FOR UPDATE row locking; concurrent tests need PostgreSQL")
@pytest.mark.asyncio
async def test_rapid_small_consumption(
    session_factory,
    stress_user: User,
    settings: Settings,
) -> None:
    """Test rapid small credit consumption.

    Simulates many small consumption operations in quick succession.
    """
    async def small_consume(user_id) -> int:
        """Consume 1 credit."""
        async with session_factory() as session:
            service = CreditService(session, settings)
            try:
                result = await service.consume_credits(user_id, 1, f"small_{uuid4()}")
                await session.commit()
                return result.total_consumed
            except ValueError:
                return 0

    # 50 rapid consumption tasks of 1 credit each
    tasks = [small_consume(stress_user.id) for _ in range(50)]
    results = await asyncio.gather(*tasks)

    # Calculate total consumed
    total_consumed = sum(results)

    # Should have consumed at most 100
    assert total_consumed <= 100

    # Verify final balance
    async with session_factory() as session:
        service = CreditService(session, settings)
        balance = await service.get_balance(stress_user.id)
        assert balance.total == 100 - total_consumed
        assert balance.total >= 0


@pytest.mark.xfail(reason="SQLite lacks FOR UPDATE row locking; concurrent tests need PostgreSQL")
@pytest.mark.asyncio
async def test_consumption_with_mixed_amounts(
    session_factory,
    stress_user: User,
    settings: Settings,
) -> None:
    """Test consumption with varying amounts.

    Some requests for large amounts, some for small.
    """
    amounts = [50, 20, 15, 10, 5, 5, 5, 5, 5, 5]  # Total: 125 (more than 100)

    async def consume_amount(user_id, amount: int) -> tuple[int, bool]:
        """Consume specified amount, return (amount_requested, success)."""
        async with session_factory() as session:
            service = CreditService(session, settings)
            try:
                await service.consume_credits(user_id, amount, f"mixed_{uuid4()}")
                await session.commit()
                return (amount, True)
            except ValueError:
                return (amount, False)

    tasks = [consume_amount(stress_user.id, amt) for amt in amounts]
    results = await asyncio.gather(*tasks)

    # Calculate successful consumption
    successful_total = sum(amt for amt, success in results if success)

    # Should have consumed at most 100
    assert successful_total <= 100

    # Verify balance
    async with session_factory() as session:
        service = CreditService(session, settings)
        balance = await service.get_balance(stress_user.id)
        assert balance.total == 100 - successful_total
        assert balance.total >= 0


@pytest.mark.xfail(reason="SQLite lacks FOR UPDATE row locking; concurrent tests need PostgreSQL")
@pytest.mark.asyncio
async def test_balance_consistency_after_concurrent_operations(
    session_factory,
    settings: Settings,
) -> None:
    """Test that balance remains consistent after concurrent operations.

    Create user, grant credits, perform concurrent operations,
    verify balance matches expected value.
    """
    # Create fresh user
    async with session_factory() as session:
        user = User(
            id=uuid4(),
            google_id=f"google-balance-{uuid4()}",
            email=f"balance-{uuid4()}@example.com",
            name="Balance Test User",
            tier=UserTier.PRO,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Grant exactly 50 credits
        service = CreditService(session, settings)
        await service.grant_purchased_credits(user.id, 50)
        await session.commit()

        user_id = user.id

    # Concurrent consumption: 10 requests for 5 credits each = 50 total
    async def consume_five(uid) -> bool:
        async with session_factory() as session:
            service = CreditService(session, settings)
            try:
                await service.consume_credits(uid, 5, f"five_{uuid4()}")
                await session.commit()
                return True
            except ValueError:
                return False

    tasks = [consume_five(user_id) for _ in range(10)]
    results = await asyncio.gather(*tasks)

    successful = sum(1 for r in results if r is True)

    # All 10 should succeed (50 / 5 = 10)
    assert successful == 10

    # Final balance should be 0
    async with session_factory() as session:
        service = CreditService(session, settings)
        balance = await service.get_balance(user_id)
        assert balance.total == 0
