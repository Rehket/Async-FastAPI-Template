"""User Setup

Revision ID: b43a90d68ea8
Revises: 
Create Date: 2019-12-09 21:40:25.911282

"""
from alembic import op
from sqlalchemy import text
from config import POSTGRES_SCHEMA


# revision identifiers, used by Alembic.
revision = 'b43a90d68ea8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        text(
            f"""
                CREATE TABLE {POSTGRES_SCHEMA}.user
                (
                    id serial primary key,
                    full_name varchar(255) null,
                    email varchar(255) not null unique,
                    hashed_password varchar null,
                    is_active bool null,
                    is_superuser bool null,
                    sys_revision integer not null, -- This is populated in the trigger.
                    sys_created_date timestamptz not null, -- This is populated in the trigger.
                    sys_modified_date timestamptz not null -- This is populated in the trigger.
                );
                -- Create Function for Auto incrementing the sys_revision field and timestamps.  
                CREATE OR REPLACE FUNCTION {POSTGRES_SCHEMA}.verify_revision_and_modified_date_for_insert() 
                RETURNS "trigger" AS $BODY$
                BEGIN
                    IF 
                        (New.sys_revision IS NOT NULL) 
                        OR  (New.sys_modified_date IS NOT NULL) 
                        OR (New.sys_created_date IS NOT NULL) THEN
                        RAISE EXCEPTION 'cannot change audit data: sys_revision, sys_modified_date, sys_created_date'; 
                    END IF;
                    New.sys_revision = 1;
                    New.sys_created_date = now();
                    New.sys_modified_date = now();
                    return New;
                END;
                $BODY$
                LANGUAGE plpgsql;

                COMMENT ON FUNCTION {POSTGRES_SCHEMA}.verify_revision_and_modified_date_for_insert()
                IS 'Function for ensuring the system values are not modified.';

                -- Create Function for preventing inserts that block .  
                CREATE OR REPLACE FUNCTION {POSTGRES_SCHEMA}.increment_revision_and_modified_date() 
                RETURNS "trigger" AS $BODY$
                BEGIN
                    IF 
                        (Old.sys_revision <> New.sys_revision) 
                        OR  (Old.sys_modified_date <> New.sys_modified_date) 
                        OR (Old.sys_created_date <> New.sys_created_date) THEN
                        RAISE EXCEPTION 'cannot change audit data: sys_revision, sys_modified_date, sys_created_date'; 
                    END IF;

                    IF (OLD.* IS DISTINCT FROM NEW.*) THEN
                        New.sys_revision = Old.sys_revision + 1;
                        New.sys_modified_date = now();
                    END IF;

                    return New;
                END;
                $BODY$
                LANGUAGE plpgsql;

                COMMENT ON FUNCTION {POSTGRES_SCHEMA}.increment_revision_and_modified_date()
                IS 'Function for Auto incrementing the sys_revision field and timestamps called from before trigger.
                The values are only updated if the contents has changed.';

                -- Create Trigger on insert
                CREATE TRIGGER {POSTGRES_SCHEMA}_user_revision_verify BEFORE INSERT 
                ON {POSTGRES_SCHEMA}.user FOR EACH ROW
                EXECUTE PROCEDURE {POSTGRES_SCHEMA}.verify_revision_and_modified_date_for_insert();

                COMMENT ON TRIGGER {POSTGRES_SCHEMA}_user_revision_verify ON {POSTGRES_SCHEMA}.user
                IS 'before insert trigger to verify revision and sys timestamps.';         

                -- Create Trigger on update
                CREATE TRIGGER {POSTGRES_SCHEMA}_user_revision_auto_increment BEFORE UPDATE 
                ON {POSTGRES_SCHEMA}.user FOR EACH ROW
                EXECUTE PROCEDURE {POSTGRES_SCHEMA}.increment_revision_and_modified_date();

                COMMENT ON TRIGGER {POSTGRES_SCHEMA}_user_revision_auto_increment ON {POSTGRES_SCHEMA}.user
                IS 'before trigger to autoincrement sys_revision and update timestamps.';
            """
        )
    )


def downgrade():
    conn = op.get_bind()
    conn.execute(
        text(
            f"""
                DROP TABLE {POSTGRES_SCHEMA}.user CASCADE;
                DROP FUNCTION {POSTGRES_SCHEMA}.increment_revision_and_modified_date CASCADE;
                DROP FUNCTION {POSTGRES_SCHEMA}.verify_revision_and_modified_date_for_insert CASCADE;
            """
        )
    )
