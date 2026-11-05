import datetime
import pytz
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL, TIMEZONE

tz = pytz.timezone(TIMEZONE)
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_now():
    return datetime.datetime.now(tz)

class AcademicTask(Base):
    __tablename__ = "academic_tasks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    course_name = Column(String)
    task_name = Column(String)
    activity_type = Column(String)
    deadline = Column(DateTime)
    status = Column(String, default="Belum dikerjakan")
    priority = Column(String, default="Sedang")

class DailyAgenda(Base):
    __tablename__ = "daily_agendas"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String)
    agenda_type = Column(String)
    start_time = Column(DateTime)

class DebtRecord(Base):
    __tablename__ = "debt_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    type = Column(String) # UTANG / PIUTANG
    person_name = Column(String)
    amount = Column(Float)
    due_date = Column(DateTime, nullable=True)
    status = Column(String, default="Belum dibayar")

def init_db():
    Base.metadata.create_all(bind=engine)