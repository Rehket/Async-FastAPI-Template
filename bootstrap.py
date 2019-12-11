# Used to bootstrap a dev environment.

import os
import sys
import config
from tenacity import retry, wait_fixed, after_log, before_sleep_log
import docker
from psycopg2 import connect
from config import logger
import alembic.command
import alembic.config
import asyncio
from databases import Database
from time import sleep
import logging

docker_client = docker.from_env()


def my_before_sleep(retry_state):
    if retry_state.attempt_number < 1:
        logger.info(
            f" 'Retrying {retry_state.fn}: attempt {retry_state.attempt_number} ended with: {retry_state.outcome}"
        )
    else:
        logger.warning(
            f" 'Retrying {retry_state.fn}: attempt {retry_state.attempt_number} ended with: {retry_state.outcome}"
        )


@retry(wait=wait_fixed(3), before_sleep=my_before_sleep)
def check_database_health():
    logger.info("Attempting DB Health Check")
    with connect(
        host=config.POSTGRES_SERVER,
        dbname="postgres",
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
        port=config.POSTGRES_PORT,
    ) as connection:
        connection.autocommit = True
        with connection.cursor() as cur:
            cur.execute(f"SELECT 1")

    print("Database is up")


def setup_database(database_name: str = "postgres"):
    with connect(
        host=config.POSTGRES_SERVER,
        dbname=database_name,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
        port=config.POSTGRES_PORT,
    ) as connection:
        connection.autocommit = True
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT datname FROM pg_database WHERE datname = '{config.POSTGRES_DB}'"
            )
            val = cur.fetchone()
            if val is None:
                logger.info(f"Database not found, creating {config.POSTGRES_DB}")
                cur.execute(f"CREATE DATABASE {config.POSTGRES_DB};")
                setup_database(database_name=config.POSTGRES_DB)
            else:
                logger.info(f"Database Found!, {config.POSTGRES_DB}")
                if database_name == "postgres":
                    setup_database(database_name=config.POSTGRES_DB)
                else:
                    cur.execute(
                        f"CREATE SCHEMA IF NOT EXISTS {config.POSTGRES_SCHEMA};"
                    )


def run_dev_bootstrap():
    # Make Sure it is dev
    my_containers = [
        x for x in docker_client.containers.list() if x.name == config.POSTGRES_SERVER
    ]

    if len(my_containers) > 0:
        logger.info(
            f"Removing container <{my_containers[0].name}: {my_containers[0].id}> "
        )
        my_containers[0].remove(force=True)

    # Set up Docker Containers
    postgres_container = docker_client.containers.run(
        image="postgres",
        ports={"5432/tcp": int(config.POSTGRES_PORT)},
        environment={
            "POSTGRES_PASSWORD": config.POSTGRES_PASSWORD,
            "POSTGRES_USER": config.POSTGRES_USER,
            "POSTGRES_DB": "postgres",
        },
        auto_remove=True,
        name=config.POSTGRES_SERVER,
        detach=True,
    )

    # Check it.
    check_database_health()
    setup_database()

    alembic.command.upgrade(alembic.config.Config("alembic.ini"), "head")
    # Pull Data From S3


async def setup_initial_users(async_db: Database):
    from app.users.crud import get_by_email
    from app.core.security import get_password_hash

    logger.info("Creating initial user!")
    user = await get_by_email(async_db=async_db, email=config.FIRST_SUPERUSER)
    if not user:
        await async_db.execute(
            query=f"INSERT INTO {config.POSTGRES_SCHEMA}.user(email, hashed_password, is_active, is_superuser) VALUES (:email, :hashed_password, :is_active, :is_superuser)",
            values={
                "email": config.FIRST_SUPERUSER,
                "hashed_password": get_password_hash(config.FIRST_SUPERUSER_PASSWORD),
                "is_active": True,
                "is_superuser": True,
            },
        )


async def run_main():

    if config.getenv_boolean("LOCAL_DEV"):
        logger.warning(
            "Starting Local Bootstrap! You have 30 seconds to cancel this operation!"
        )
        sleep(30)
        run_dev_bootstrap()

    elif not config.getenv_boolean("LOCAL_DEV"):
        logger.warning("Remote not setup yet!")

    else:
        raise EnvironmentError("LOCAL_DEV environment variable must be set.")

    async with Database(config.SQLALCHEMY_DATABASE_URI) as database:
        await setup_initial_users(database)

if __name__ == "__main__":

    asyncio.run(run_main())
