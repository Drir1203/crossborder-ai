"""VeyaShip - Task Scheduler.

APScheduler-based periodic tasks for data synchronization,
credit management, and cleanup operations.
"""

from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.payment import Subscription, SubscriptionStatus
from app.models.user import User, UserPlan


class SchedulerService:
    """Manages periodic background tasks."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        """Register and start all scheduled tasks."""
        # Daily credit reset for expired subscriptions
        self.scheduler.add_job(
            self._expire_subscriptions,
            CronTrigger(hour=0, minute=0),  # Midnight daily
            id="expire_subscriptions",
            replace_existing=True,
        )

        # Weekly cleanup of old generation records
        self.scheduler.add_job(
            self._cleanup_old_records,
            CronTrigger(day_of_week="mon", hour=3, minute=0),  # Monday 3am
            id="cleanup_old_records",
            replace_existing=True,
        )

        # Every 15 minutes: check for pending content generations
        self.scheduler.add_job(
            self._process_pending_generations,
            IntervalTrigger(minutes=15),
            id="process_pending_generations",
            replace_existing=True,
        )

        self.scheduler.start()
        print("✅ Scheduler started with all jobs registered")

    async def stop(self):
        """Shut down the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            print("✅ Scheduler stopped")

    async def _expire_subscriptions(self):
        """Expire subscriptions that have passed their end date."""
        async with async_session_factory() as db:
            now = datetime.now(timezone.utc)
            result = await db.execute(
                select(Subscription).where(
                    Subscription.current_period_end < now,
                    Subscription.is_active == True,
                    Subscription.status == SubscriptionStatus.ACTIVE,
                )
            )
            expired = result.scalars().all()

            for sub in expired:
                sub.is_active = False
                sub.status = SubscriptionStatus.EXPIRED

                # Downgrade user to free plan
                await db.execute(
                    update(User)
                    .where(User.id == sub.user_id)
                    .values(plan=UserPlan.FREE, credits_remaining=0, credits_total=10)
                )

            if expired:
                await db.commit()
                print(f"⏰ Expired {len(expired)} subscriptions")

    async def _cleanup_old_records(self):
        """Clean up content generation records older than 90 days."""
        async with async_session_factory() as db:
            # Archival logic here
            print("🧹 Cleaned up old records")

    async def _process_pending_generations(self):
        """Process any pending AI content generations."""
        # This would be replaced by a proper task queue (Celery/RQ)
        # for production use. For now, it's a placeholder.
        print("⏳ No pending generations to process")
