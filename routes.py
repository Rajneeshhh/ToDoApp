from fastapi import APIRouter, Depends, Form, HTTPException, Request, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from core import queries
from core.models import User
from schemas import TaskCreate, TaskUpdate, TaskOut
from fastapi.templating import Jinja2Templates
from utils.logger import logger
from typing import List
from fastapi.security import OAuth2PasswordBearer
from schemas import Token, UserCreate, UserLogin
from auth import create_access_token, create_refresh_token, verify_token
from core.db import get_session

router = APIRouter()


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





oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/register", response_model=Token)
async def register(user: UserCreate, session: AsyncSession = Depends(get_session)):
    # Check if user exists
    result = await session.execute(select(User).filter_by(username=user.username))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Create new user
    new_user = User(username=user.username, password=user.password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)  # fetch back from DB

    access_token = create_access_token({"sub": new_user.username})
    refresh_token = create_refresh_token({"sub": new_user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@router.post("/login", response_model=Token)
async def login(user: UserLogin, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        text("SELECT * FROM users WHERE username=:username AND password=:password"),
        {"username": user.username, "password": user.password}
    )
    db_user = result.fetchone()
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh(refresh_token: str = Body(...)):
    username = verify_token(refresh_token)
    access_token = create_access_token({"sub": username})
    new_refresh_token = create_refresh_token({"sub": username})
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    return {"message": f"Hello {username}, you are authorized!"}
