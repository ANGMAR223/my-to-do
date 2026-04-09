from fastapi import FastAPI
from app.database import engine, Base
from app.task import router as task
import logging

import uvicorn

from contextlib import asynccontextmanager

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log', encoding='utf-8')
        ]
    )
    
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    
    logger.info('Приложение запускается')
    logger.info('База данный запущена')
    
    yield
    
    await engine.dispose()
    
    logger.info('Приложение завершило работу')
    logger.info('База данных закрыта')
        
app = FastAPI(lifespan=lifespan)
app.include_router(task)

if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, host='0.0.0.0', reload=True, loop="asyncio")