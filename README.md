# FastAPI Template

Минимальный шаблон FastAPI-сервиса с асинхронным SQLAlchemy, Alembic, Redis,
SAQ-воркером, JWT-аутентификацией и DI на `that-depends`.

## Стек

- Python 3.13
- FastAPI + Uvicorn
- SQLAlchemy 2 (async) + Alembic + PostgreSQL (asyncpg)
- Redis + SAQ (фоновый воркер)
- Pydantic v2 + pydantic-settings
- DI: `that-depends`
- Аутентификация: JWT + refresh-сессии + cookie
- Линтеры: ruff, mypy, pyright
- Пакетный менеджер: [uv](https://docs.astral.sh/uv/)

## Структура

```
app/
  asgi.py            # ASGI entrypoint
  __init__.py        # create_app, router wiring
  worker.py          # SAQ worker settings
  bg_jobs/           # фоновые задачи (хуки)
  core/              # config, DI container, db middleware, redis client
  dependencies/      # FastAPI dependencies
  models/            # SQLAlchemy модели (User, Session)
  repos/             # репозитории (BaseRepo, SoftDeletableRepo)
  resources/         # строки, исключения, openapi
  schemas/           # pydantic-схемы
  services/          # бизнес-сервисы (Auth, JWT, Session, User)
  utils/             # утилиты (cookies, pagination, time)
  views/             # роуты (/auth/sign-in, /refresh, /logout)
alembic/             # миграции (пустые)
tests/               # pytest + factories
```

## Запуск локально

```sh
uv sync
cp .env_example .env
docker compose up -d postgres redis
uv run alembic upgrade head
uv run uvicorn app.asgi:app --reload
```

## Команды

```sh
make install        # uv sync
make run            # запустить uvicorn с reload
make migrate        # alembic upgrade head
make revision m="..." # alembic revision --autogenerate
make lint           # ruff + mypy + pyright
make format         # ruff format + fix
make docker-test    # тесты в docker
```
