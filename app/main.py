# Назначение файла:
# Главная точка входа FastAPI-приложения: конфигурация, маршруты, статика, обработчики ошибок.

# Импортируем системные инструменты для работы с окружением.
import os

# Импортируем FastAPI для создания веб-приложения.
from fastapi import FastAPI, Request
# Импортируем обработчик ошибок HTTP.
from fastapi.responses import HTMLResponse
# Импортируем поддержку статических файлов.
from fastapi.staticfiles import StaticFiles
# Импортируем шаблоны Jinja2.
from fastapi.templating import Jinja2Templates
# Импортируем middleware для cookie-сессий.
from starlette.middleware.sessions import SessionMiddleware
# Импортируем загрузчик переменных окружения.
from dotenv import load_dotenv

# Импортируем маршруты страниц.
from app.routes import pages_router
# Импортируем REST API.
from app.rest import api_router

# Загружаем переменные окружения из .env (если файл существует).
load_dotenv()

# Создаём экземпляр FastAPI.
app = FastAPI(title='Fast-API-Learn', version='1.0.0')

# Готовим шаблонизатор для глобального использования (например, в 404).
templates = Jinja2Templates(directory='templates')

# Подключаем middleware сессий для админки.
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv('SESSION_SECRET', 'change_me_super_secret'),
    max_age=60 * 60 * 24 * 30,  # 30 дней
    same_site='lax',
    https_only=False,
)

# Подключаем маршруты страниц и REST API.
app.include_router(pages_router)
app.include_router(api_router)

# Подключаем статические файлы.
app.mount('/static', StaticFiles(directory='static'), name='static')

# Пользовательская страница 404.
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    # Рендерим шаблон 404.
    return templates.TemplateResponse('404.html', {'request': request}, status_code=404)
