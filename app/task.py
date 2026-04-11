from fastapi import APIRouter, Depends, status, HTTPException
from app.database import get_db
from app.models import Task
from app.schemas import CreateTask, TaskResponse, UpdataTask
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Задачи"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(create_task: CreateTask, db: AsyncSession = Depends(get_db)) -> TaskResponse:

    logger.info(f"Попытка создать задачу: {create_task}")

    update_task = Task(
        title=create_task.title,
        description=create_task.description,
        is_completed=create_task.is_completed,
        deadline=create_task.deadline,
        priority=create_task.priority,
    )

    if create_task.deadline is not None and create_task.deadline < date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Дедлайн не может быть в прошлом",
        )

    try:

        db.add(update_task)
        await db.commit()
        await db.refresh(update_task)

        logger.info("Задача успешно создана")

        return update_task

    except Exception as e:

        logger.error(f"Ошибка при создании задачи: {e}")

        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка создания задачи"
        )


@router.get("/", summary="Получить все задачи", response_model=List[TaskResponse])
async def get_all_tasks(
    db: AsyncSession = Depends(get_db), sort_by: str = "id", show_completed: bool = True
) -> List[TaskResponse]:
    logger.info(f"Попытка получить все задачи из базы данных. Фильтр: {sort_by}")

    try:
        query = select(Task)

        if not show_completed:
            query = query.where(Task.is_completed == False)

        if sort_by == "priority":
            query = query.order_by(Task.priority.desc(), Task.deadline.nullslast())
        elif sort_by == "deadline":
            query = query.order_by(Task.deadline.asc().nullslast(), Task.priority.desc())
        elif sort_by == "created_at":
            query = query.order_by(Task.created_at.desc())
        else:
            query = query.order_by(Task.id.desc())

        result = await db.execute(query)
        all_tasks = result.scalars().all()

        logger.info(f"Все задачи успешно получены. Фильтр: {sort_by}")

        return all_tasks

    except Exception as e:

        logger.error(f"Ошибка при попытке получить все задачи {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка получения задач"
        )


@router.get("/today", response_model=List[TaskResponse], summary="Задачи на сегодня")
async def get_today_tasks(db: AsyncSession = Depends(get_db)):
    today = date.today()
    query = (
        select(Task)
        .where(Task.deadline == today, Task.is_completed == False)
        .order_by(Task.priority.desc())
    )

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/upcoming", response_model=List[TaskResponse], summary="Ближайшие задачи")
async def get_upcoming_tasks(db: AsyncSession = Depends(get_db), days: int = 7):
    today = date.today()
    end_date = today + timedelta(days=days)

    query = (
        select(Task)
        .where(Task.deadline.between(today, end_date))
        .order_by(Task.deadline.asc(), Task.priority.desc())
    )

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/overdue", response_model=List[TaskResponse], summary="Просроченные задачи")
async def get_overdue_tasks(db: AsyncSession = Depends(get_db)):
    today = date.today()
    query = (
        select(Task)
        .where(Task.deadline < today, Task.is_completed == False)
        .order_by(Task.deadline.asc())
    )

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{task_id}", response_model=TaskResponse, summary="Получить задачу из БД по id")
async def get_task_by_id(task_id: int, db: AsyncSession = Depends(get_db)) -> TaskResponse:
    logger.info(f"Попытка получить задачу по id {task_id}")

    try:
        query = select(Task).where(task_id == Task.id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Задача с id {task_id} не найдена"
            )

        logger.info(f"Задача по id {task_id} успешно получена")

        return task

    except HTTPException:
        raise

    except Exception as e:

        logger.error(f"Ошибка при получение задачи по id {task_id} - {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка получения задачи"
        )


@router.delete("/{task_id}", summary="Удаление задачи из БД")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)) -> Dict:
    logger.info(f"Попытка удалить задачу с id {task_id}")

    try:

        query = select(Task).where(Task.id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Задача с id {task_id} не найдена"
            )

        await db.delete(task)
        await db.commit()

        delete_info = {"id": task.id, "title": task.title, "description": task.description}

        logger.info(f"Задача по id {task_id} успешно удалена")

        return {"id": task_id, "task_delete": delete_info, "deleted_at": datetime.now()}

    except HTTPException:
        raise

    except Exception as e:

        logger.error(f"Ошибка при удаление задачи по id {task_id}")

        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении задачи: {str(e)}",
        )


@router.put("/{task_id}", response_model=TaskResponse, summary="Полное обновление задачи")
async def update_task(task_id: int, update_task: UpdataTask, db: AsyncSession = Depends(get_db)):
    logger.info(f"Попытка обновить задачу по id {task_id}")

    try:
        query = select(Task).where(Task.id == task_id)
        result = await db.execute(query)
        task = result.scalar_one_or_none()

        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Задача с id {task_id} не найдена"
            )

        task.title = update_task.title
        task.description = update_task.description
        task.is_completed = update_task.is_completed
        task.deadline = update_task.deadline
        task.priority = update_task.priority

        await db.commit()
        await db.refresh(task)

        logger.info(f"Задача по id {task_id} успешно обновлена")

        return task

    except HTTPException:
        raise

    except Exception as e:

        logger.error(f"Ошибка при обновлении задачи по id {task_id} - {e}")

        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при обновлении отеля"
        )
