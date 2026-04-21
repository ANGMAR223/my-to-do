from fastapi import Header, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.database import get_db
from app.models import User

logger = logging.getLogger(__name__)


async def get_current_user(
    x_telegram_id: int = Header(..., alias="X-Telegram-ID"), db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(User).where(User.telegram_id == x_telegram_id))

    user = result.scalar_one_or_none()

    if not user:

        user = User(telegram_id=x_telegram_id, user_name=None, first_name=None)
        logger.info(f"Создан новый пользователь с Telegram ID: {x_telegram_id}")

        try:

            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(
                f"Создан новый пользователь с telegram_id={x_telegram_id}, внутренний id={user.id}"
            )

        except Exception as e:

            logger.error(f"Ошибка при сохранении нового пользователя: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при сохранении пользователя",
            )

    else:
        logger.debug(f"Пользователь найден: telegram_id={x_telegram_id}, id={user.id}")

    return user
