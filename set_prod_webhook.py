import asyncio
import os
from dotenv import load_dotenv
from app.bot.bot_instance import get_bot

load_dotenv()

PRODUCTION_URL = "https://my-todo-api-ono2.onrender.com"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"
FULL_WEBHOOK_URL = f"{PRODUCTION_URL}{WEBHOOK_PATH}"

async def main():
    bot = get_bot()
    print(f"Устанавливаю вебхук: {FULL_WEBHOOK_URL}")
    await bot.set_webhook(FULL_WEBHOOK_URL)
    print("Вебхук установлен.")
    info = await bot.get_webhook_info()
    print(f"Информация о вебхуке: url={info.url}, pending_update_count={info.pending_update_count}")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
    