import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv
from models import Base  # Update with the correct import path for your models

# ✅ Load environment variables
load_dotenv()

# ✅ Use sync database engine
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://candidate_user:candidate_password@localhost/candidate_db")

# ✅ Configure Alembic
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# ✅ Logging config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ Metadata for migrations
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in offline mode"""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in online mode"""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
