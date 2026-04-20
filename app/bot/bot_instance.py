from dotenv import load_dotenv
import os
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram import Bot, Dispatcher
from app.bot.handlers import router
from aiogram.fsm.storage.memory import MemoryStorage

import logging

logger = logging.getLogger(__name__)

load_dotenv()

WORKER_URL = "https://telegram-proxy.wngarinech.workers.dev"


def get_bot():

    custom_api_server = TelegramAPIServer.from_base(WORKER_URL)

    BOT_TOKEN = os.getenv("BOT_TOKEN")

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не задан в .env")

    return Bot(token=BOT_TOKEN, session=AiohttpSession(), api_server=custom_api_server)


def get_dispatcher():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    return dp
