import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

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
    return Task(
        id=uuid4(),
        title="Test Task",
        description="Test Description",
        status=Status.created,
    )


def make_mock_result(tasks_list):
    """Helper to mock query results."""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = tasks_list
    mock_result.scalars.return_value.first.return_value = (
        tasks_list[0] if tasks_list else None
    )
    return mock_result


@pytest.mark.asyncio
async def test_get_tasks_success(mock_db, sample_task):
    """Тест успешного получения задач"""
    mock_result = make_mock_result([sample_task])
    mock_db.execute.return_value = mock_result

    tasks = await TaskService.get_tasks(mock_db)

    assert len(tasks) == 1
    assert tasks[0].id == sample_task.id
    assert tasks[0].title == sample_task.title
    assert tasks[0].status == sample_task.status
    mock_db.execute.assert_called_once()
    args, _ = mock_db.execute.call_args
    assert isinstance(args[0], type(select(Task)))


@pytest.mark.asyncio
async def test_get_tasks_empty(mock_db):
    """Тест получения пустого списка задач"""
    mock_result = make_mock_result([])
    mock_db.execute.return_value = mock_result

    tasks = await TaskService.get_tasks(mock_db)
    assert tasks == []
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_tasks_database_error(mock_db):
    """Тест ошибки базы данных при получении задач"""
    mock_db.execute.side_effect = SQLAlchemyError("Database error")
    with pytest.raises(SQLAlchemyError):
        await TaskService.get_tasks(mock_db)


@pytest.mark.asyncio
async def test_get_task_success(mock_db, sample_task):
    """Тест успешного получения задачи"""
    task_id = str(sample_task.id)
    with patch.object(
        TaskService, "_get_task_or_raise", AsyncMock(return_value=sample_task)
    ):
        task = await TaskService.get_task(mock_db, task_id)
        assert task.id == sample_task.id
        TaskService._get_task_or_raise.assert_called_once_with(
            mock_db, task_id
        )


@pytest.mark.asyncio
async def test_get_task_not_found(mock_db):
    """Тест получения несуществующей задачи"""
    task_id = str(uuid4())
    with patch.object(
        TaskService,
        "_get_task_or_raise",
        AsyncMock(side_effect=TaskNotFoundError("Not found")),
    ):
        with pytest.raises(TaskNotFoundError):
            await TaskService.get_task(mock_db, task_id)


@pytest.mark.asyncio
async def test__get_task_or_raise_success(mock_db, sample_task):
    """Тест успешного получения задачи по ID"""
    task_id = str(sample_task.id)
    mock_result = make_mock_result([sample_task])
    mock_db.execute.return_value = mock_result

    task = await TaskService._get_task_or_raise(mock_db, task_id)

    assert task.id == sample_task.id
    assert task.status == sample_task.status
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test__get_task_or_raise_not_found(mock_db):
    """Тест неуспешного получения задачи по ID"""
    task_id = str(uuid4())
    mock_result = make_mock_result([])
    mock_db.execute.return_value = mock_result

    with pytest.raises(TaskNotFoundError):
        await TaskService._get_task_or_raise(mock_db, task_id)


@pytest.mark.asyncio
async def test__get_task_or_raise_invalid_uuid(mock_db):
    """Тест неуспешного получения задачи по недопустимому UUID"""
    invalid_task_id = "invalid-uuid"
    with pytest.raises(TaskNotFoundError):
        await TaskService._get_task_or_raise(mock_db, invalid_task_id)


@pytest.mark.asyncio
async def test__get_task_or_raise_database_error(mock_db):
    """Тест ошибки базы данных при получении задачи по ID"""
    task_id = str(uuid4())
    mock_db.execute.side_effect = SQLAlchemyError("Database error")
    with pytest.raises(SQLAlchemyError):
        await TaskService._get_task_or_raise(mock_db, task_id)
