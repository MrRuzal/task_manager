from fastapi import APIRouter, Depends, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.services.task_service import TaskService
from app.database import get_db


router = APIRouter()


@router.get(
    "/", response_model=list[TaskResponse], status_code=status.HTTP_200_OK
)
async def get_tasks(db: Session = Depends(get_db)):
    tasks = await TaskService.get_tasks(db)
    return tasks


@router.post(
    "/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED
)
async def create_task(task_create: TaskCreate, db: Session = Depends(get_db)):
    task = await TaskService.create_task(db, task_create)
    return task


@router.get(
    "/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK
)
async def get_task(task_id: UUID, db: Session = Depends(get_db)):
    task = await TaskService.get_task(db, task_id)
    return task


@router.patch(
    "/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK
)
async def update_task(
    task_id: UUID, task_update: TaskUpdate, db: Session = Depends(get_db)
):
    task = await TaskService.update_task(db, task_id, task_update)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, db: Session = Depends(get_db)):
    await TaskService.delete_task(db, task_id)
