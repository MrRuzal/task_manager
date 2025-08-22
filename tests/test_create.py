import pytest
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.future import select

from app.models import Task, Status
from app.schemas import TaskCreate, TaskUpdate
from app.services.task_service import TaskService
from app.exceptions import TaskNotFoundError, TaskAlreadyExistsError


@pytest.fixture
def mock_db():
    """Фикстура для мока базы данных"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_task_create():
    """Фикстура с примером схемы создания задачи"""
    sample_task_data = {
        "title": "Test Task",
        "description": "Test Description",
    }
    return TaskCreate(**sample_task_data)


@pytest.fixture
def sample_task(sample_task_create):
    """Фикстура с примером задачи"""
    task_id = uuid4()
    return Task(
        id=task_id,
        title=sample_task_create.title,
        description=sample_task_create.description,
        status=Status.created,
    )


@pytest.mark.asyncio
async def test_create_task_success(mock_db, sample_task_create, sample_task):
    """Тест успешного создания задачи"""
    mock_db.add = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    with patch('app.services.task_service.Task', return_value=sample_task):
        result = await TaskService.create_task(mock_db, sample_task_create)

        mock_db.add.assert_called_once_with(sample_task)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(sample_task)
        assert result == sample_task


@pytest.mark.asyncio
async def test_create_task_integrity_error(mock_db, sample_task_create):
    """Тест ошибки целостности при создании задачи"""
    mock_db.add = AsyncMock()
    mock_db.commit = AsyncMock(
        side_effect=IntegrityError("Integrity error", None, None)
    )
    mock_db.rollback = AsyncMock()

    with patch('app.services.task_service.Task', return_value=AsyncMock()):
        with pytest.raises(TaskAlreadyExistsError):
            await TaskService.create_task(mock_db, sample_task_create)

        mock_db.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_create_task_database_error(mock_db, sample_task_create):
    """Тест общей ошибки базы данных при создании задачи"""
    mock_db.add = AsyncMock()
    mock_db.commit = AsyncMock(side_effect=SQLAlchemyError("Database error"))
    mock_db.rollback = AsyncMock()

    with patch('app.services.task_service.Task', return_value=AsyncMock()):
        with pytest.raises(SQLAlchemyError):
            await TaskService.create_task(mock_db, sample_task_create)

        mock_db.rollback.assert_called_once()
