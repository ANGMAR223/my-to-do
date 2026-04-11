from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date

class CreateTask(BaseModel):
    
    title: str = Field(
        ...,
        max_length=100,
        json_schema_extra={'example': 'Создать пет проект'}
    )
    
    description: Optional[str] = Field(
        None,
        max_length= 300,
        json_schema_extra={'example': 'Создать to-do практически самому без помощи AI'}
    )
    
    is_completed: Optional[bool] = Field(
        None,
        json_schema_extra={'example': False}
    )
    
    deadline: Optional[date] = Field(
        None,
        json_schema_extra={'example': '2026-12-31'},
        description='Дата дедлайна в формате YYYY-MM-DD'
    )
    
    priority: Optional[int] = Field(
        2,
        ge=1,
        le=3,
        json_schema_extra={'example': 2},
        description='1 - низкий, 2 - средний, 3 - высокий'
    )

class UpdataTask(CreateTask):
    pass

class TaskResponse(BaseModel):
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    is_completed: bool
    description: Optional[str]
    created_at: datetime
    deadline: Optional[date]
    priority: int
    