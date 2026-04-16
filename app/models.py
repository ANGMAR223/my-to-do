from app.database import Base
from sqlalchemy import Column, String, DateTime, Integer, func, Boolean, Date, CheckConstraint


class Task(Base):

    __tablename__ = "task"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    title = Column(String(150), index=True, nullable=False)

    description = Column(String(300), nullable=True, index=True)

    is_completed = Column(Boolean, default=False, index=True)

    created_at = Column(DateTime, server_default=func.now())

    deadline = Column(Date, nullable=True)

    priority = Column(Integer, default=2, nullable=False, index=True)

    __table_args__ = (
        CheckConstraint("priority >= 1 AND priority <=3", name="check_priority_range"),
    )
