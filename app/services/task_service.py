from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.future import select

from app.common.logs import logger
from app.exceptions import TaskNotFoundError, TaskAlreadyExistsError
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate


class TaskService:
    @staticmethod
    async def _get_task_or_raise(db: AsyncSession, task_id: str) -> Task:
        try:
            task_uuid = UUID(task_id)
        except ValueError as e:
            logger.error(f"Invalid UUID format for task_id {task_id}: {e}")
            raise TaskNotFoundError(f"Task with id {task_id} not found") from e
        try:
            result = await db.execute(
                select(Task).filter(Task.id == task_uuid)
            )
            task = result.scalars().first()
            if not task:
                raise TaskNotFoundError(f"Task with id {task_id} not found")
            return task
        except SQLAlchemyError as e:
            logger.error(f"Database error on _get_task_or_raise: {e}")
            raise

    @staticmethod
    async def get_tasks(db: AsyncSession) -> List[Task]:
        try:
            result = await db.execute(select(Task))
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Database error on get_tasks: {e}")
            raise

    @staticmethod
    async def get_task(db: AsyncSession, task_id: str) -> Task:
        return await TaskService._get_task_or_raise(db, task_id)

    @staticmethod
    async def create_task(db: AsyncSession, task_create: TaskCreate) -> Task:
        task = Task(**task_create.model_dump())
        db.add(task)
        try:
            await db.commit()
            await db.refresh(task)
            return task
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error on create_task: {e}")
            raise TaskAlreadyExistsError(
                "Task with this UUID already exists"
            ) from e
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error on create_task: {e}")
            raise

    @staticmethod
    async def update_task(
        db: AsyncSession, task_id: str, task_update: TaskUpdate
    ) -> Task:
        try:
            task = await TaskService._get_task_or_raise(db, task_id)
            for key, value in task_update.model_dump(
                exclude_unset=True
            ).items():
                setattr(task, key, value)
            await db.commit()
            await db.refresh(task)
            return task
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error on update_task: {e}")
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error on update_task: {e}")
            raise

    @staticmethod
    async def delete_task(db: AsyncSession, task_id: str) -> UUID:
        try:
            task = await TaskService._get_task_or_raise(db, task_id)
            await db.delete(task)
            await db.commit()
            return task.id
        except TaskNotFoundError:
            logger.error(f"Task with id {task_id} not found for deletion")
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error on delete_task: {e}")
            raise
