import asyncio
from datetime import date, datetime
from core import queries
from core.db import get_session


def test_create_and_get_task():
    async def run():
        async for session in get_session():
            # Create
            task_id = await queries.create_task(
                session,
                title="Test Task",
                description="Testing existing DB",
                due_date=date(2025, 9, 15),
                priority=3,
                status="Pending",
            )
            # Get
            task = await queries.get_task_by_id(session, task_id)
            return task

    task = asyncio.run(run())

    assert task["title"] == "Test Task"
    assert task["priority"] == 3
    assert task["status"] == "Pending"
    assert task["due_date"].startswith("2025-09-15")


def test_update_task():
    async def run():
        async for session in get_session():
            task_id = await queries.create_task(session, title="Old Task")
            await queries.update_task(
                session,
                task_id=task_id,
                title="Updated Task",
                status="Completed",
                completed_at=datetime(2025, 9, 15, 12, 30),
            )
            return await queries.get_task_by_id(session, task_id)

    task = asyncio.run(run())

    assert task["title"] == "Updated Task"
    assert task["status"] == "Completed"
    assert task["completed_at"].startswith("2025-09-15 12:30")


def test_delete_task():
    async def run():
        async for session in get_session():
            task_id = await queries.create_task(session, title="Delete Me")
            await queries.delete_task(session, task_id)
            return await queries.get_task_by_id(session, task_id)

    task = asyncio.run(run())

    assert task is None


def test_get_all_tasks():
    async def run():
        async for session in get_session():
            await queries.create_task(session, title="Task 1")
            await queries.create_task(session, title="Task 2")
            return await queries.get_all_tasks(session)

    tasks = asyncio.run(run())
    titles = [t["title"] for t in tasks]
    assert "Task 1" in titles
    assert "Task 2" in titles
