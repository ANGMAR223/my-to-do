from sqlalchemy.orm import relationship

from app.database import Base
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    DateTime,
    Integer,
    func,
    Boolean,
    Date,
    CheckConstraint,
    BigInteger,
)


class Task(Base):

    __tablename__ = "task"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    title = Column(String(150), index=True, nullable=False)

    description = Column(String(300), nullable=True, index=True)

    is_completed = Column(Boolean, default=False, index=True)

    created_at = Column(DateTime, server_default=func.now())

    deadline = Column(Date, nullable=True)

    priority = Column(Integer, default=2, nullable=False, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    user = relationship("User", back_populates="tasks")

    __table_args__ = (
        CheckConstraint("priority >= 1 AND priority <=3", name="check_priority_range"),
    )


class User(Base):
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    
    user_name = Column(String(100), nullable=True, index=True)
    
    first_name = Column(String(100), nullable=True, index=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
