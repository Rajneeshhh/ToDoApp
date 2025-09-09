# app/core/queries.py
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def create_task(session: AsyncSession,title: str,description: str = "",due_date: str = None,priority: int = 2,status: str = "Pending",):
    result = await session.execute(text("""INSERT INTO tasks 
                        (title, description, due_date, priority, status)
                        VALUES (:title, :description, :due_date, :priority, :status)
                        """),{"title": title,
                        "description": description,
                        "due_date": due_date,
                        "priority": priority,
                        "status": status,
                    },
                )
    await session.commit()
    return result.lastrowid



async def get_all_tasks(session: AsyncSession):
    result = await session.execute(text("SELECT * FROM tasks ORDER BY created_at DESC"))
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]


async def get_task_by_id(session: AsyncSession, task_id: int):
    result = await session.execute(text("SELECT * FROM tasks WHERE task_id = :task_id"),
        {"task_id": task_id},)
    row = result.fetchone()
    return dict(row._mapping) if row else None


async def update_task(
    session: AsyncSession,
    task_id: int,
    title: str = None,
    description: str = None,
    due_date: str = None,
    priority: int = None,
    status: str = None,
    completed_at: str = None,
):
    fields = []
    params = {"task_id": task_id}

    if title is not None:
        fields.append("title = :title")
        params["title"] = title
    if description is not None:
        fields.append("description = :description")
        params["description"] = description
    if due_date is not None:
        fields.append("due_date = :due_date")
        params["due_date"] = due_date
    if priority is not None:
        fields.append("priority = :priority")
        params["priority"] = priority
    if status is not None:
        fields.append("status = :status")
        params["status"] = status
    if completed_at is not None:
        fields.append("completed_at = :completed_at")
        params["completed_at"] = completed_at

    if not fields:
        return False

    query = f"UPDATE tasks SET {', '.join(fields)} WHERE task_id = :task_id"
    await session.execute(text(query), params)
    await session.commit()
    return True


async def delete_task(session: AsyncSession, task_id: int):
    await session.execute(text("DELETE FROM tasks WHERE task_id = :task_id"),
                            {"task_id": task_id},)
    await session.commit()
    return True
