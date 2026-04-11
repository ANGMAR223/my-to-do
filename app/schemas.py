from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

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
    
class UpdataTask(CreateTask):
    pass
    
    
class TaskResponse(BaseModel):
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    is_completed: bool
    description: Optional[str]
    created_at: datetime
    