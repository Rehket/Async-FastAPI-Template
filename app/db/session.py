from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import config

engine = create_engine(
    config.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    connect_args={"options": f"-csearch_path={config.POSTGRES_SCHEMA}"},
)
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
