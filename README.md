# task-manager

Веб-приложение для управления задачами на FastAPI с асинхронным доступом к PostgreSQL. Проект позволяет создавать, получать, изменять и удалять задачи. 

## Технологии

- Python 3.13
- FastAPI
- PostgreSQL
- SQLAlchemy (async)
- Alembic (миграции)
- Docker и docker-compose
- Pytest (тестирование)

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/MrRuzal/task-manager.git
   cd task-manager
   ```

2. Создайте файл `.env` на основе `.env.example` и укажите параметры подключения к БД.

3. Запустите приложение через Docker Compose:
   ```bash
   docker-compose up --build
   ```
   Миграции Alembic применяются автоматически при старте контейнера.

## Документация API

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Тестирование

Для запуска тестов выполните:
```bash
pytest
```

## Автор

[MrRuzal](https://github.com/MrRuzal)