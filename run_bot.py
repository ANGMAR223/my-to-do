import logging
import asyncio
from app.bot.bot_instance import get_bot, get_dispatcher

logger = logging.getLogger(__name__)

async def main():
    logger.info("Бот запускается")
    bot = get_bot()
    dp = get_dispatcher()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())