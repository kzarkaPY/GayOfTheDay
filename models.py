from sqlalchemy import create_engine, Column, Integer, String, BigInteger, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    run_count = Column(Integer, default=0)
    pidor_count = Column(Integer, default=0)
    sosal_count = Column(BigInteger, default=0)

class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True)
    season_number = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

class SeasonStats(Base):
    __tablename__ = "season_stats"

    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    username = Column(String, nullable=True)
    run_count = Column(Integer, default=0)
    pidor_count = Column(Integer, default=0)
    sosal_count = Column(BigInteger, default=0)

class CommandUsage(Base):
    __tablename__ = "command_usage"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, nullable=False)
    command = Column(String, nullable=False)
    last_used = Column(DateTime, nullable=False)

class SeasonControl(Base):
    __tablename__ = "season_control"

    id = Column(Integer, primary_key=True)
    last_clear = Column(DateTime, nullable=True)
    current_season = Column(Integer, default=0)
    is_active = Column(Boolean, default=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
