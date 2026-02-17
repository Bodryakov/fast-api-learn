# Структура проекта Fast-API-Learn

Ниже приведена согласованная структура проекта и краткое описание назначения каждого файла и каталога.

```
.
├─ app/
│  ├─ main.py
│  ├─ routes.py
│  ├─ rest.py
│  ├─ supabase_client.py
│  ├─ admin_auth.py
│  └─ models.py
├─ templates/
│  ├─ base.html
│  ├─ index.html
│  ├─ section.html
│  ├─ lesson.html
│  ├─ admin_login.html
│  ├─ admin.html
│  └─ 404.html
├─ static/
│  ├─ css/
│  │  └─ style.css
│  └─ js/
│     ├─ app.js
│     ├─ admin.js
│     └─ tiptap.js
├─ sql/
│  ├─ schema.sql
│  └─ seed.sql
├─ .env.example
├─ Procfile
└─ requirements.txt
```

## Описание файлов и каталогов

- `app/` — корневой каталог backend-приложения FastAPI.
- `app/main.py` — точка входа: создание FastAPI-приложения, подключение маршрутов, конфигурация шаблонов, статики и обработчиков ошибок.
- `app/routes.py` — маршруты серверного рендеринга (страницы разделов, уроков, админки, 404).
- `app/rest.py` — REST API для CRUD-операций с разделами, уроками, тестами и задачами.
- `app/supabase_client.py` — подключение к Supabase и общие функции доступа к базе и Storage.
- `app/admin_auth.py` — логика аутентификации администратора и работы с сессией.
- `app/models.py` — схемы данных (Pydantic) для валидации входящих/исходящих данных.

- `templates/` — HTML-шаблоны Jinja2 для серверного рендеринга.
- `templates/base.html` — базовый шаблон с общими блоками (header, темы, подключение CSS/JS).
- `templates/index.html` — главная страница со списком разделов и уроков (карточки).
- `templates/section.html` — страница конкретного раздела со списком уроков.
- `templates/lesson.html` — страница конкретного урока (теория, тесты, задачи, навигация).
- `templates/admin_login.html` — страница входа в админ-панель.
- `templates/admin.html` — интерфейс админ-панели (CRUD и Tiptap).
- `templates/404.html` — пользовательская страница ошибки 404.

- `static/` — статические файлы фронтенда.
- `static/css/style.css` — стили проекта (Material, темы, адаптив, Grid).
- `static/js/app.js` — логика интерфейса сайта (навигация, тесты, темы).
- `static/js/admin.js` — логика админ-панели (CRUD, сохранение, валидация).
- `static/js/tiptap.js` — инициализация редактора Tiptap и загрузка изображений.

- `sql/` — SQL-скрипты для Supabase.
- `sql/schema.sql` — создание таблиц, связей, индексов и расширений.
- `sql/seed.sql` — заполнение базы тестовыми данными (2 раздела, 2 урока).

- `.env.example` — пример переменных окружения для запуска.
- `Procfile` — команда запуска приложения для деплоя на Koyeb.
- `requirements.txt` — зависимости Python для backend и деплоя.
