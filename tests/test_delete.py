import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.models import Task, Status
from app.services.task_service import TaskService
from app.exceptions import TaskNotFoundError


@pytest.fixture
def mock_db():
    """Фикстура для мока базы данных"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_task():
    """Фикстура с примером задачи"""
    task_id = uuid4()
    return Task(
        id=task_id,
        title="Test Task",
        description="Test Description",
        status=Status.created,
    )


@pytest.mark.asyncio
async def test_delete_task_success(mock_db, sample_task):
    """Тест успешного удаления задачи"""
    task_id = str(sample_task.id)

    with patch.object(
        TaskService, '_get_task_or_raise', AsyncMock(return_value=sample_task)
    ):
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock()

        result = await TaskService.delete_task(mock_db, task_id)

        assert result == sample_task.id
        mock_db.delete.assert_called_once_with(sample_task)
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_task_not_found(mock_db):
    """Тест несуществующей задачи при удалении"""
    task_id = str(uuid4())

    with patch.object(
        TaskService,
        '_get_task_or_raise',
        AsyncMock(side_effect=TaskNotFoundError("Not found")),
    ):
        with pytest.raises(TaskNotFoundError):
            await TaskService.delete_task(mock_db, task_id)


@pytest.mark.asyncio
async def test_delete_task_database_error(mock_db, sample_task):
    """Тест ошибки базы данных при удалении задачи"""
    task_id = str(sample_task.id)

    with patch.object(
        TaskService, '_get_task_or_raise', AsyncMock(return_value=sample_task)
    ):
        mock_db.delete = AsyncMock()
        mock_db.commit = AsyncMock(
            side_effect=SQLAlchemyError("Database error")
        )
        mock_db.rollback = AsyncMock()

        with pytest.raises(SQLAlchemyError):
            await TaskService.delete_task(mock_db, task_id)

        mock_db.rollback.assert_called_once()
