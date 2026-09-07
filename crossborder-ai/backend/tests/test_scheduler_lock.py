"""VeyaShip - 定时任务跨进程锁测试

背景：生产是 uvicorn 4 worker，每个 worker 各跑一份 APScheduler。
若不加锁，整店巡检（写 StoreCheckLog）会在 4 个 worker 各执行一遍。

覆盖：
1. SQLite 开发模式（单进程）下 _run_with_lock 直接执行 job
2. 两个写数据 job 的包装方法确实带正确的锁 key
"""

import pytest


@pytest.mark.asyncio
async def test_run_with_lock_sqlite_executes_job():
    """SQLite 模式单进程，无需锁，job 正常执行。"""
    from app.services.scheduler import SchedulerService

    svc = SchedulerService()
    calls = []

    async def fake_job():
        calls.append(1)

    await svc._run_with_lock("test_key", fake_job)
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_run_with_lock_no_op_job_runs():
    """job 抛异常前正常执行，锁包层不吞错误。"""
    from app.services.scheduler import SchedulerService

    svc = SchedulerService()

    async def returns_value():
        return "done"

    # 不应抛异常（SQLite 路径直接透传）
    await svc._run_with_lock("test_key2", returns_value)


@pytest.mark.asyncio
async def test_locked_wrappers_use_correct_lock_key(monkeypatch):
    """写数据 job 的包装方法都经过 _run_with_lock，且锁 key 唯一。

    注：订阅过期任务已在 scheduler 重构中随 Subscription 模型移除，
    当前写数据包装为「定时整店巡检」与「Agent 任务分发」两个。
    """
    from app.services.scheduler import SchedulerService

    svc = SchedulerService()
    captured = []

    async def fake_lock(lock_key, job):
        captured.append(lock_key)

    monkeypatch.setattr(svc, "_run_with_lock", fake_lock)

    await svc._run_store_checks_locked()
    await svc._dispatch_agent_tasks()

    assert captured == ["store_check_daily", "dispatch_agent_tasks"]
    # 两个 job 用不同的锁 key，互不阻塞
    assert len(set(captured)) == 2
