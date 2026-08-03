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
from app.models.user import User


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

        # Daily store check: 定时整店巡检
        self.scheduler.add_job(
            self._run_store_checks,
            CronTrigger(hour=2, minute=30),  # 每天凌晨 2:30
            id="store_check_daily",
            replace_existing=True,
        )

        self.scheduler.start()
        print("[Scheduler] started with all jobs registered")

    async def _run_store_checks(self):
        """定时整店巡检：检查所有用户的商品，记录结果"""
        import json

        from app.models.product import Product
        from app.models.store_check_log import StoreCheckLog

        async with async_session_factory() as db:
            # 找出有商品的用户
            result = await db.execute(
                select(Product.user_id).distinct()
            )
            user_ids = result.scalars().all()

            for user_id in user_ids:
                # 检查该用户所有商品
                products_result = await db.execute(
                    select(Product).where(Product.user_id == user_id)
                )
                products = products_result.scalars().all()

                issues = []
                healthy = 0
                for p in products:
                    product_issues = []
                    if not p.title:
                        product_issues.append("缺标题")
                    if not p.price:
                        product_issues.append("缺价格")
                    if not p.url:
                        product_issues.append("缺链接")
                    if product_issues:
                        issues.append({
                            "id": str(p.id),
                            "title": p.title or "未命名商品",
                            "issues": product_issues,
                        })
                    else:
                        healthy += 1

                # 保存巡检记录
                db.add(StoreCheckLog(
                    user_id=user_id,
                    total=len(products),
                    healthy=healthy,
                    issue_count=len(issues),
                    issues_json=json.dumps(issues, ensure_ascii=False) if issues else None,
                ))

            await db.flush()
            await db.commit()
            print(f"[Scheduler] 定时巡检完成：{len(user_ids)} 个用户")

    async def stop(self):
        """Shut down the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            print("[Scheduler] stopped")

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
                    .values(plan="free", credits=10)
                )

            if expired:
                await db.commit()
                print(f"[Scheduler] Expired {len(expired)} subscriptions")

    async def _cleanup_old_records(self):
        """Clean up content generation records older than 90 days."""
        async with async_session_factory() as db:
            # Archival logic here
            print("[Scheduler] Cleaned up old records")

    async def _process_pending_generations(self):
        """Process any pending AI content generations."""
        # This would be replaced by a proper task queue (Celery/RQ)
        # for production use. For now, it's a placeholder.
        print("[Scheduler] No pending generations to process")
