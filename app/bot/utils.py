from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import httpx
import logging

from app.bot.config import API_BASE_URL

logger = logging.getLogger(__name__)

def get_main_keyboard():

    keyboard = [[KeyboardButton(text="📋 Мои задачи"), KeyboardButton(text="➕ Новая задача")]]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


async def create_task_in_api(task_data: dict) -> dict | None:
    url = f"{API_BASE_URL}/tasks/"
    payload = {**task_data, "user_id": 1}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка API: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Ошибка сети: {e}")
        return None