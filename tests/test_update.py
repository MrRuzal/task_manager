import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.models import Task, Status
from app.schemas import TaskUpdate
from app.services.task_service import TaskService
from app.exceptions import TaskNotFoundError


@pytest.fixture
def mock_db():
    """Фикстура для мока базы данных"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_task_data():
    """Фикстура с примерными данными задачи"""
    return {
        "title": "Test Task",
        "description": "Test Description",
    }


@pytest.fixture
def sample_task(sample_task_data):
    """Фикстура с примером задачи"""
    task_id = uuid4()
    return Task(
        id=task_id,
        title=sample_task_data["title"],
        description=sample_task_data["description"],
        status=Status.created,
    )


@pytest.fixture
def sample_task_update():
    """Фикстура с примером схемы обновления задачи"""
    return TaskUpdate(
        title="Updated Task",
        description="Updated Description",
        status=Status.in_progress,
    )


@pytest.fixture
def patch_get_task(sample_task):
    """Фикстура для патча метода получения задачи"""
    with patch.object(
        TaskService, '_get_task_or_raise', AsyncMock(return_value=sample_task)
    ) as mock:
        yield mock


@pytest.mark.asyncio
async def test_update_task_success(
    mock_db, sample_task_update, patch_get_task, sample_task
):
    """Тест успешного обновления задачи"""
    task_id = str(sample_task.id)

    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    result = await TaskService.update_task(
        mock_db, task_id, sample_task_update
    )

    assert result.title == sample_task_update.title
    assert result.description == sample_task_update.description
    assert result.status == sample_task_update.status

    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(sample_task)


@pytest.mark.asyncio
async def test_update_task_partial(mock_db, sample_task, patch_get_task):
    """Тест частичного обновления задачи"""

    class TaskUpdatePartial(TaskUpdate):
        title: str = None
        description: str = None
        status: Status = None

    partial_update = TaskUpdatePartial(title="Partial Update")
    task_id = str(sample_task.id)

    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    result = await TaskService.update_task(mock_db, task_id, partial_update)

    assert result.title == "Partial Update"
    assert result.description == sample_task.description
    assert result.status == sample_task.status


@pytest.mark.asyncio
async def test_update_task_not_found(mock_db, sample_task_update):
    """Тест обновления несуществующей задачи"""
    task_id = str(uuid4())

    with patch.object(
        TaskService,
        '_get_task_or_raise',
        AsyncMock(side_effect=TaskNotFoundError("Not found")),
    ):
        with pytest.raises(TaskNotFoundError):
            await TaskService.update_task(mock_db, task_id, sample_task_update)


@pytest.mark.asyncio
async def test_update_task_database_error(
    mock_db, sample_task_update, patch_get_task
):
    """Тест ошибки базы данных при обновления задачи"""
    task_id = str(patch_get_task.return_value.id)

    mock_db.commit = AsyncMock(side_effect=SQLAlchemyError("Database error"))
    mock_db.rollback = AsyncMock()

    with pytest.raises(SQLAlchemyError):
        await TaskService.update_task(mock_db, task_id, sample_task_update)

    mock_db.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_update_task_partial_database_error(
    mock_db, sample_task, patch_get_task
):
    """Тест ошибки базы данных при частичном обновлении задачи"""

    class TaskUpdatePartial(TaskUpdate):
        title: str = None
        description: str = None
        status: Status = None

    partial_update = TaskUpdatePartial(title="Partial Update")
    task_id = str(sample_task.id)

    mock_db.commit = AsyncMock(side_effect=SQLAlchemyError("Database error"))
    mock_db.rollback = AsyncMock()

    with pytest.raises(SQLAlchemyError):
        await TaskService.update_task(mock_db, task_id, partial_update)

    mock_db.rollback.assert_called_once()
