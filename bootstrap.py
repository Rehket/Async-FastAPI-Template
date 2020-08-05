# Used to bootstrap a dev environment.

import config
from tenacity import retry, wait_fixed
from psycopg2 import connect
from config import logger
import alembic.command
import alembic.config
import asyncio
from databases import Database



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

    run_dev_bootstrap()

    async with Database(config.SQLALCHEMY_DATABASE_URI) as database:
        await setup_initial_users(database)

if __name__ == "__main__":

    asyncio.run(run_main())
