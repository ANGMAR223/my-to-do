"""
Скрипт для удаления вебхука Telegram.
Используется для локального тестирования через long polling.
"""
import asyncio
from app.bot.bot_instance import get_bot

async def main():
    bot = get_bot()
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Вебхук удалён. Можно запускать polling локально.")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())