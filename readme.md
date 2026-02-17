# Fast-API-Learn

Минималистичное full-stack веб-приложение для обучения основам FastAPI.

## Общее описание
Fast-API-Learn — это учебный проект, демонстрирующий создание современного веб-приложения на FastAPI с использованием Supabase в качестве БД и хранилища. Frontend реализован на чистом HTML, CSS и VanillaJS без фреймворков.

## Особенности
- **Backend**: FastAPI с полной CRUD-логикой
- **База данных**: Supabase (PostgreSQL + Storage)
- **Frontend**: HTML, CSS Grid, Material Design, тёмная/светлая тема
- **Админка**: Редактор Tiptap для создания уроков, загрузка изображений в Supabase Storage
- **Безопасность**: CSRF-токены, sanitize HTML, cookie-сессии
- **Деплой**: Docker и Koyeb-ready

## Технологический стек
| Слой | Технология |
|------|------------|
| Backend | FastAPI 0.111+, Python 3.11 |
| БД / Storage | Supabase (PostgreSQL 15 + PostgREST + Storage) |
| Frontend | VanillaJS, CSS Grid, Material-дизайн, Tiptap (ESM CDN) |
| Шаблоны | Jinja2 |
| Безопасность | CSRF-токены, sanitize HTML (bleach), cookie-сессии 30 дней |
| Деплой | Docker, Koyeb, Uvicorn |

## Структура проекта
```
.
├─ app/                    # Backend FastAPI
│  ├─ main.py             # Точка входа, конфигурация приложения
│  ├─ routes.py           # SSR-страницы (главная, разделы, уроки, админка)
│  ├─ rest.py             # REST API CRUD + загрузка изображений
│  ├─ supabase_client.py  # Клиент Supabase, запросы к БД и Storage
│  ├─ admin_auth.py       # Аутентификация администратора, CSRF
│  └─ models.py           # Pydantic-схемы для валидации
├─ templates/              # Jinja2-шаблоны
├─ static/                 # Статические файлы frontend
│  ├─ css/style.css       # Стили, Material Design, темы
│  └─ js/                 # JavaScript (app.js, admin.js, tiptap.js)
├─ sql/                    # SQL-скрипты для Supabase
│  ├─ schema.sql          # Создание таблиц, индексов, триггеров
│  └─ seed.sql            # Тестовые данные (2 раздела × 2 урока)
├─ requirements.txt        # Зависимости Python
├─ Dockerfile             # Docker-образ
├─ Procfile               # Команда запуска для Koyeb
└─ .env                   # Переменные окружения
```

## Архитектура данных

### Таблицы Supabase
- **sections**: разделы курса
- **lessons**: уроки с JSONB-контентом (теория, тесты, задачи, изображения)

### JSONB-контент урока
```json
{
  "theory": {"title": "...", "html": "...", "images": [...]},
  "tests": [{"question": "...", "options": [...], "correct_index": 0..3}],
  "tasks": [{"title": "...", "html": "..."}],
  "images": ["lesson-images/abc.png"]
}
```

### Supabase Storage
Бакет `lesson-images` для хранения изображений уроков с публичным доступом.

## Маршруты и функциональность

### Публичные страницы
- `/` — главная страница со списком разделов и уроков
- `/section-{n}-{slug}` — страница раздела
- `/section-{n}-{slug}/lesson-{m}-{slug}` — страница урока с теорией, тестами и задачами
- `/404` — страница ошибки

### Админка (доступ по `/bod`)
- `/bod` — форма входа (логин/пароль из `.env`)
- `/bod/dashboard` — панель управления (CRUD разделов и уроков)
- `/bod/section/create|edit/{id}` — создание/редактирование раздела
- `/bod/lesson/create|edit/{id}` — создание/редактирование урока с редактором Tiptap

### REST API (требует авторизации)
- `GET|POST|PUT|DELETE /api/sections` — управление разделами
- `GET|POST|PUT|DELETE /api/lessons` — управление уроками
- `POST /api/upload-image` — загрузка изображений (≤5 МБ)

## Установка и запуск

### Локальный запуск
```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd fast-api-learn

# 2. Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
.\venv\Scripts\Activate.ps1  # Windows

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env, добавив свои данные Supabase

# 5. Примените SQL-скрипты в Supabase Dashboard
# - Выполните sql/schema.sql
# - Выполните sql/seed.sql

# 6. Запустите приложение
uvicorn app.main:app --reload
```

### Docker
```bash
# Сборка образа
docker build -t fast-api-learn .

# Запуск контейнера
docker run -p 8000:8000 --env-file .env fast-api-learn
```

### Деплой на Koyeb
1. Подключите GitHub-репозиторий к Koyeb
2. Установите переменные окружения в панели Koyeb
3. Приложение будет автоматически деплоиться при push в main-ветку

## Переменные окружения
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_PASSWORD=your-service-role-key
ADMIN_LOGIN=your-admin-login
ADMIN_PASSWORD=your-admin-password
SESSION_SECRET=your-session-secret
CSRF_SECRET=your-csrf-secret
STORAGE_BUCKET=lesson-images
```

## Безопасность
- CSRF-токены на все POST/PUT/DELETE-запросы
- Очистка HTML от XSS (bleach)
- Валидация slug: только строчные латинские буквы и дефисы
- Сессии с подписью и сроком 30 дней
- Автоматическое удаление изображений при удалении урока

## Тестовые данные
После применения `seed.sql` доступны:
- Раздел 1: «Введение в FastAPI» (2 урока)
- Раздел 2: «Маршруты и ответы» (2 урока)

Каждый урок содержит теорию, 4 теста и 2 задачи.

## Команды
```bash
# Запуск локального сервера
uvicorn app.main:app --reload

# Активация виртуального окружения (Windows)
.\venv\Scripts\Activate.ps1

# Установка зависимостей
pip install -r requirements.txt
```

## Лицензия
MIT