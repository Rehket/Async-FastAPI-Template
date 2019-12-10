# Used to bootstrap a dev environment.

import os
import subprocess
import sys
from app.core import config
from tenacity import retry, wait_fixed
import docker
from psycopg2 import connect


docker_client = docker.from_env()


@retry(wait=wait_fixed(2))
def check_database_health():
    print("Attempting DB Health Check")
    with connect(
            host=config.POSTGRES_SERVER,
            dbname=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            port=config.POSTGRES_PORT,
    ) as connection:
        connection.autocommit = True
        with connection.cursor() as cur:
            cur.execute(f"SELECT 1")

    print("Database is up")


if __name__ == "__main__":

    if not os.environ.get("LOCAL_DEV", False):
        print(
            "This is configured for local development only. If you want to run this, you must set LOCAL_DEV to True"
        )
        sys.exit()

    my_containers = [x for x in docker_client.containers.list() if x.name == "integrator_dev"]

    if len(my_containers) > 0:
        print(f"Removing container <{my_containers[0].name}: {my_containers[0].id}> ")
        my_containers[0].remove(force=True)

    # Set up Docker Containers
    postgres_container = docker_client.containers.run(
        image="postgres",
        ports={"5432/tcp": int(config.POSTGRES_PORT)},
        environment={
            "POSTGRES_PASSWORD": config.POSTGRES_PASSWORD,
            "POSTGRES_USER": config.POSTGRES_USER,
            "POSTGRES_DB": config.POSTGRES_DB,
        },
        auto_remove=True,
        name="integrator_dev",
        detach=True,
    )

    check_database_health()

    with connect(
        host=config.POSTGRES_SERVER,
        dbname=config.POSTGRES_DB,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
        port=config.POSTGRES_PORT,
    ) as connection:
        connection.autocommit = True
        with connection.cursor() as cur:
            cur.execute(f"CREATE SCHEMA {config.POSTGRES_SCHEMA}")
