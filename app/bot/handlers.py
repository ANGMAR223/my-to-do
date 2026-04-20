
from aiogram import types, F, Router
from aiogram.filters import CommandStart
from app.bot.utils import get_main_keyboard, create_task_in_api

from app.bot.states import AddTaskState
from aiogram.fsm.context import FSMContext

import logging

router = Router()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("bot_log.log", encoding="utf-8")],
)

logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(
        "Привет! Я to-do бот. Ты можешь добавлять, редактировать и удалять задачи.",
        reply_markup=get_main_keyboard(),
    )


@router.message(F.text == "📋 Мои задачи")
async def my_tasks(message: types.Message):
    await message.answer("Здесь будут отображаться ваши задачи.")


@router.message(F.text == "➕ Новая задача")
async def new_task(message: types.Message, state: FSMContext):
    await state.set_state(AddTaskState.waiting_for_title)
    await message.answer("📝 Введи название задачи (или напиши /cancel для отмены):")


@router.message(AddTaskState.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddTaskState.waiting_for_description)
    await message.answer("📄 Введи описание задачи (или напиши /skip, чтобы пропустить):")


@router.message(AddTaskState.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    description = message.text if message.text != "/skip" else None
    await state.update_data(description=description)
    await state.set_state(AddTaskState.waiting_for_deadline)
    await message.answer("📅 Введи дедлайн в формате ГГГГ-ММ-ДД (например, 2026-12-31) или /skip:")


@router.message(AddTaskState.waiting_for_deadline)
async def process_deadline(message: types.Message, state: FSMContext):
    deadline = message.text if message.text != "/skip" else None
    await state.update_data(deadline=deadline)
    await state.set_state(AddTaskState.waiting_for_priority)
    await message.answer("🔢 Введи приоритет (1-низкий, 2-средний, 3-высокий) или /skip (будет 2):")


@router.message(AddTaskState.waiting_for_priority)
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
            f"✅ Задача успешно создана!\n" 
            f"📌 {task_data['title']}\n" 
            f"🔢 Приоритет: {priority}"
        )

    await state.clear()


@router.message(F.text)
async def unknown_message(message: types.Message):
    await message.answer("🤔 Я не знаю такой команды. Воспользуйся кнопками на клавиатуре.")

