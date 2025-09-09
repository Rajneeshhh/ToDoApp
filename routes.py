from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from core import queries
from schemas import TaskCreate, TaskUpdate, TaskOut
from fastapi.templating import Jinja2Templates
from utils.logger import logger
from typing import List


router = APIRouter()
templates = Jinja2Templates(directory="templates")
base_url = "http://127.0.0.1:8000/tasks/api/"

@router.post("/api/", response_model=TaskOut)
async def create_task(task: TaskCreate, session: AsyncSession = Depends(get_session)):
    try:
        task_id = await queries.create_task(
            session,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            priority=task.priority,
            status=task.status,
        )
        new_task = await queries.get_task_by_id(session, task_id)
        logger.info(f"Task created: {new_task}")
        return new_task
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/", response_model=List[TaskOut])
async def list_tasks(session: AsyncSession = Depends(get_session)):
    try:
        tasks = await queries.get_all_tasks(session)
        logger.info(f"Fetched {len(tasks)} tasks")
        return tasks
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, session: AsyncSession = Depends(get_session)):
    try:
        task = await queries.get_task_by_id(session, task_id)
        if not task:
            logger.warning(f"Task not found with ID {task_id}")
            raise HTTPException(status_code=404, detail="Task not found")
        logger.info(f"Fetched task: {task}")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/api/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, task: TaskUpdate, session: AsyncSession = Depends(get_session)):
    try:
        updated = await queries.update_task(
            session,
            task_id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            priority=task.priority,
            status=task.status,
            completed_at=task.completed_at,
        )
        if not updated:
            logger.warning(f"No update applied or task not found: ID {task_id}")
            raise HTTPException(status_code=404, detail="Task not found or no update applied")

        updated_task = await queries.get_task_by_id(session, task_id)
        logger.info(f"Task updated: {updated_task}")
        return updated_task
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/api/{task_id}")
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session)):
    try:
        task = await queries.get_task_by_id(session, task_id)
        if not task:
            logger.warning(f"Task not found for deletion: ID {task_id}")
            raise HTTPException(status_code=404, detail="Task not found")

        await queries.delete_task(session, task_id)
        logger.info(f"Task deleted: ID {task_id}")
        return {"message": "Task deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Frontend routes for Crud operations
@router.get("/tasks", response_class=HTMLResponse)
async def list_tasks_page(request: Request):
    async for session in get_session():
        tasks = await queries.get_all_tasks(session)
        break 
    
    return templates.TemplateResponse(
        "list_tasks.html", 
        {
            "request": request,
            "tasks": tasks,
            "base_url": base_url
        }
    )

@router.get("/create-task", response_class=HTMLResponse)
async def create_task_page(request: Request):
    return templates.TemplateResponse("add_task.html", {"request": request})

@router.get("/update-task", response_class=HTMLResponse)
async def update_task_page(request: Request):
    return templates.TemplateResponse("update.html", {"request": request})

@router.get("/delete", response_class=HTMLResponse)
async def delete_task_page(request: Request):
    return templates.TemplateResponse("delete.html", {"request": request})
