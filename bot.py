import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import API_BASE_URL
import httpx
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("bot_log.log", encoding="utf-8")],
)

logger = logging.getLogger(__name__)

load_dotenv()

WORKER_URL = "https://telegram-proxy.wngarinech.workers.dev"

custom_api_server = TelegramAPIServer.from_base(WORKER_URL)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in the environment variables.")

bot = Bot(token=BOT_TOKEN, session=AiohttpSession(), api_server=custom_api_server)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class AddTaskState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_deadline = State()
    waiting_for_priority = State()


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


def get_main_keyboard():

    keyboard = [[KeyboardButton(text="📋 Мои задачи"), KeyboardButton(text="➕ Новая задача")]]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(
        "Привет! Я эхо-бот. Напиши мне что-нибудь, и я повторю.", reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "📋 Мои задачи")
async def my_tasks(message: types.Message):
    await message.answer("Здесь будут отображаться ваши задачи.")


@dp.message(F.text == "➕ Новая задача")
async def new_task(message: types.Message, state: FSMContext):
    await state.set_state(AddTaskState.waiting_for_title)
    await message.answer("📝 Введи название задачи (или напиши /cancel для отмены):")


@dp.message(AddTaskState.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddTaskState.waiting_for_description)
    await message.answer("📄 Введи описание задачи (или напиши /skip, чтобы пропустить):")


@dp.message(AddTaskState.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    description = message.text if message.text != "/skip" else None
    await state.update_data(description=description)
    await state.set_state(AddTaskState.waiting_for_deadline)
    await message.answer("📅 Введи дедлайн в формате ГГГГ-ММ-ДД (например, 2026-12-31) или /skip:")


@dp.message(AddTaskState.waiting_for_deadline)
async def process_deadline(message: types.Message, state: FSMContext):
    deadline = message.text if message.text != "/skip" else None
    await state.update_data(deadline=deadline)
    await state.set_state(AddTaskState.waiting_for_priority)
    await message.answer("🔢 Введи приоритет (1-низкий, 2-средний, 3-высокий) или /skip (будет 2):")


@dp.message(AddTaskState.waiting_for_priority)
async def process_priority(message: types.Message, state: FSMContext):
    priority = 2

    if message.text != "/skip":
        try:
            priority = int(message.text)
            if priority not in [1, 2, 3]:
                raise ValueError()
        except ValueError:
            await message.answer("❌ Некорректный приоритет. Введите 1, 2, 3 или /skip.")
            return

    await state.update_data(priority=priority)
    task_data = await state.get_data()

    await message.answer("⏳ Сохраняю задачу...")

    result = await create_task_in_api(task_data)

    if result:
        await message.answer(
            f"✅ Задача успешно создана!\n" f"📌 {task_data['title']}\n" f"🔢 Приоритет: {priority}"
        )

    await state.clear()


@dp.message(F.text)
async def unknown_message(message: types.Message):
    await message.answer("🤔 Я не знаю такой команды. Воспользуйся кнопками на клавиатуре.")


async def main():
    logger.info("Бот запускается")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
