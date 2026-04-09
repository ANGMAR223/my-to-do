from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CreateTask(BaseModel):
    
    title: str = Field(
        ...,
        max_length=100,
        example='Создать пет проект'
    )
    
    description: Optional[str] = Field(
        None,
        max_length= 300,
        example='Создать to-do практически самому без помощи AI'
    )
    
    is_completed: Optional[bool] = Field(
        None,
        example=False
    )
    
class UpdataTask(CreateTask):
    pass
    
    
class TaskResponse(BaseModel):
    
    id: int
    title: str
    is_completed: bool
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True
    