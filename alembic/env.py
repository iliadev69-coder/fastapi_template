import asyncio
import logging
from collections.abc import MutableMapping
from logging.config import fileConfig
from typing import Literal

from sqlalchemy import Connection, engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context
from app.core.config import EnvSecrets
from app.models import *  # noqa: F403
from app.models import base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = base.BaseModel.metadata

log = logging.getLogger('alembic')
env = EnvSecrets()

config.set_main_option('sqlalchemy.url', EnvSecrets().DB_DSN)


def include_name(
    name: str | None,
    type_: Literal[
        'schema', 'table', 'column', 'index', 'unique_constraint', 'foreign_key_constraint'
    ],
    parent_names: MutableMapping[
        Literal['schema_name', 'table_name', 'schema_qualified_table_name'], str | None
    ],
) -> bool:
    if type_ == 'table' and name is not None:
        return name in target_metadata.tables
    return True


def run_migrations_offline() -> None:
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        include_name=include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_name=include_name,
    )

    with context.begin_transaction() as tx:
        context.run_migrations()
        if 'dry-run' in context.get_x_argument():
            log.info('Dry-run succeeded; now rolling back transaction...')
            if tx is not None:
                tx.rollback()


async def run_migrations_online() -> None:
    connectable = AsyncEngine(
        engine_from_config(
            configuration={'sqlalchemy.url': env.DB_DSN},
            prefix='sqlalchemy.',
            poolclass=pool.NullPool,
            future=True,
        ),
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
