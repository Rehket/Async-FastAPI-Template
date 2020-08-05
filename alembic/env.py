from __future__ import with_statement

import os

from alembic import context
from sqlalchemy import (
    engine_from_config,
    pool,
    MetaData,
    Table,
    ForeignKeyConstraint,
    Index,
)
from logging.config import fileConfig
from config import POSTGRES_SCHEMA, PUBLIC_TABLES
import config as app_config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

from app.db.base import Base  # noqa

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


# TODO: See if search path needs to be added here.
def get_url():
    user = app_config.POSTGRES_USER
    password = app_config.POSTGRES_PASSWORD
    server = app_config.POSTGRES_SERVER
    db = app_config.POSTGRES_DB
    port = app_config.POSTGRES_PORT
    if app_config.RDS_SSL_CONTEXT:
        return f"postgresql://{user}:{password}@{server}:{port}/{db}?sslmode=require&sslrootcert={app_config.RDS_CERTIFICATE_PATH}"
    return f"postgresql://{user}:{password}@{server}:{port}/{db}"


def include_schemas(names):
    # produce an include object function that filters on the given schemas
    def include_object(object, name, type_, reflected, compare_to):
        if type_ == "table":
            return object.schema in names
        return True

    return include_object


def lookup_correct_schema(name):
    if name in PUBLIC_TABLES:
        return "public"
    else:
        return POSTGRES_SCHEMA


def _get_table_key(name, schema):
    if schema is None:
        return name
    else:
        return schema + "." + name


def tometadata(table, metadata, schema):
    key = _get_table_key(table.name, schema)
    if key in metadata.tables:
        return metadata.tables[key]

    args = []
    for c in table.columns:
        args.append(c.copy(schema=schema))
    new_table = Table(table.name, metadata, schema=schema, *args, **table.kwargs)
    for c in table.constraints:
        if isinstance(c, ForeignKeyConstraint):
            constraint_schema = lookup_correct_schema(c.elements[0].column.table.name)
        else:
            constraint_schema = schema
        new_table.append_constraint(
            c.copy(schema=constraint_schema, target_table=new_table)
        )

    for index in table.indexes:
        # skip indexes that would be generated
        # by the 'index' flag on Column
        if len(index.columns) == 1 and list(index.columns)[0].index:
            continue
        Index(
            index.name,
            unique=index.unique,
            *[new_table.c[col] for col in index.columns.keys()],
            **index.kwargs,
        )
    return table._schema_item_copy(new_table)


meta_schemax = MetaData()
for table in target_metadata.tables.values():
    tometadata(table, meta_schemax, lookup_correct_schema(table.name))
target_metadata = meta_schemax


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        version_table_schema=POSTGRES_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration, prefix="sqlalchemy.", poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_schemas=True,  # schemas,
            version_table_schema=POSTGRES_SCHEMA,
            include_object=include_schemas([None, POSTGRES_SCHEMA])
        )
        with context.begin_transaction():

            context.execute(f"CREATE SCHEMA IF NOT EXISTS {POSTGRES_SCHEMA};")
            context.execute(f"SET search_path TO {POSTGRES_SCHEMA}")
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
