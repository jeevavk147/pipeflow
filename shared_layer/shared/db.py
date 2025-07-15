
import os
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

load_dotenv()

Base = declarative_base()

# Global DB URL
GLOBAL_DB_URL = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_SERVER')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

global_engine = create_engine(GLOBAL_DB_URL, pool_pre_ping=True)
GlobalSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=global_engine)

def get_tenant_engine(tenant_db_name: str):
    url = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_SERVER')}:{os.getenv('POSTGRES_PORT')}/{tenant_db_name}"
    return create_engine(url, pool_pre_ping=True)

from fastapi import Depends, Request
def get_db(request: Request):
    tenant_id = request.headers.get('X-Tenant-ID')
    if tenant_id:
        engine = get_tenant_engine(f"pipeflow_tenant_{tenant_id}")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
    else:
        db = GlobalSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Alembic migration helpers
from alembic.config import Config
from alembic import command
def run_alembic_upgrade(tenant_db_url, revision="head"):
    """
    Run Alembic migrations for the given tenant database URL, like 'alembic -x db_url=... upgrade head'.
    """
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))
    alembic_cfg.set_main_option("sqlalchemy.url", tenant_db_url)
    alembic_cfg.cmd_opts = type('obj', (object,), {'x': [f'db_url={tenant_db_url}']})
    command.upgrade(alembic_cfg, revision)

def migrate_masterdata(global_session, tenant_session):
    from shared.models import Pipe, Component, Fitting, Gas, Liquid, Unit
    for Model in [Pipe, Component, Fitting, Gas, Liquid, Unit]:
        records = global_session.query(Model).all()
        for record in records:
            data = {c.name: getattr(record, c.name) for c in Model.__table__.columns if c.name != 'id'}
            tenant_session.add(Model(**data))
        tenant_session.commit()
