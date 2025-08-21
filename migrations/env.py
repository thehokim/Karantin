from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Чтобы Alembic видел твои модели
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Base  # твои модели

# this is the Alembic Config object, which provides access to the values within the .ini file.
config = context.config
fileConfig(config.config_file_name)

# Подключение к БД
config.set_main_option("sqlalchemy.url", "postgresql://postgres:postgres@localhost:5432/karantin")

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
