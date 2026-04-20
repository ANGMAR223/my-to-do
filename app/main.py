from fastapi import FastAPI, Request, HTTPException
from app.database import engine, Base
from app.task import router as task
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from aiogram.types import Update
from app.bot.bot_instance import get_bot, get_dispatcher

from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log", encoding="utf-8")],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Приложение запускается")
    logger.info("База данный запущена")
    
    logger.info("Инициализация бота и диспетчера")
    bot = get_bot()
    dp = get_dispatcher()
    app.state.bot = bot
    app.state.dp = dp
    logger.info("Бот и диспетчер инициализированы")

    yield

    await engine.dispose()

    logger.info("Приложение завершило работу")
    logger.info("База данных закрыта")
    
    await bot.session.close()
    logger.info("Сессия бота закрыта")


app = FastAPI(lifespan=lifespan)
app.include_router(task)

@app.post("/webhook/{secret}")
async def webhook(secret: str, request: Request):
    
    expected_secret = os.getenv("WEBHOOK_SECRET")
    
    if not expected_secret:
        logger.error("WEBHOOK_SECRET не установлен в переменных окружения")
        raise HTTPException(status_code=500, detail="WEBHOOK_SECRET not set")
        
    if secret != expected_secret:
        logger.warning(f"Получен запрос с неверным секретом: {secret}")
        raise HTTPException(status_code=403, detail="Неверный секрет")

    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Ошибка при разборе JSON: {e}")
        raise HTTPException(status_code=400, detail="Неверный JSON")
    
    try:
        update = Update.model_validate(data)
    except Exception as e:
        logger.error(f"Ошибка при валидации данных: {e}")
        raise HTTPException(status_code=400, detail="Неверные данные")
    
    bot = app.state.bot
    dp = app.state.dp
    
    await dp.feed_update(bot, update)
    
    return {"status": "ok"}
    

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
