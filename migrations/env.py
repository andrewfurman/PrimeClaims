from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from members.member_model import Member, db
from claims.claim_model import Claim
from auth.users_model import User  # Add this line


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override the sqlalchemy.url with environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # Replace 'postgres://' with 'postgresql://' if needed
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    config.attributes['sqlalchemy.url'] = DATABASE_URL

# Set target metadata
target_metadata = db.Model.metadata

# Interpret the config file for Python logging
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except FileNotFoundError:
        # Skip logging setup if config file is not found
        pass

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    if not configuration:
        configuration = {}
    
    # Get URL from Flask app
    configuration["sqlalchemy.url"] = os.getenv("DATABASE_URL", "").replace(
        "postgres://", "postgresql://", 1
    )

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
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