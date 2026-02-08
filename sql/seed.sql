-- Назначение файла:
-- Скрипт заполняет базу тестовыми данными (2 раздела × 2 урока) на тему FastAPI.

-- Очищаем данные (для повторного запуска в dev-среде).
truncate table public.lessons restart identity cascade;
truncate table public.sections restart identity cascade;

-- Вставляем разделы.
insert into public.sections (id, number, title, slug, meta)
values
    (uuid_generate_v4(), 1, 'Введение в FastAPI', 'vvedenie-v-fastapi', '{"description":"Старт и базовые понятия"}'),
    (uuid_generate_v4(), 2, 'Маршруты и ответы', 'marshruty-i-otvety', '{"description":"Роутинг и форматирование ответов"}');

-- Вставляем уроки.
with sec as (
    select id, number, slug from public.sections
)
insert into public.lessons (section_id, number, title, slug, status, content, meta)
values
(
    (select id from sec where number = 1),
    1,
    'Что такое FastAPI',
    'chto-takoe-fastapi',
    'published',
    jsonb_build_object(
        'theory', jsonb_build_object(
            'title', 'Коротко о FastAPI',
            'html', '<p>FastAPI — современный Python-фреймворк для создания API. Он быстрый, удобный и основан на стандартах ASGI.</p><p>Ключевые преимущества: высокая производительность, удобная типизация и автогенерация документации.</p>',
            'images', jsonb_build_array('lesson-images/fastapi-logo.png')
        ),
        'tests', jsonb_build_array(
            jsonb_build_object(
                'question','На каком стандарте основан FastAPI?',
                'options', jsonb_build_array('WSGI','ASGI','CGI','SOAP'),
                'correct_index', 1
            ),
            jsonb_build_object(
                'question','Что FastAPI умеет генерировать автоматически?',
                'options', jsonb_build_array('Dockerfile','Документацию OpenAPI','SQL-миграции','HTML-верстку'),
                'correct_index', 1
            ),
            jsonb_build_object(
                'question','Основной язык разработки FastAPI?',
                'options', jsonb_build_array('JavaScript','Python','Go','PHP'),
                'correct_index', 1
            ),
            jsonb_build_object(
                'question','Какой тип производительности у FastAPI?',
                'options', jsonb_build_array('Низкая','Средняя','Высокая','Зависит от браузера'),
                'correct_index', 2
            )
        ),
        'tasks', jsonb_build_array(
            jsonb_build_object(
                'title','Установка FastAPI',
                'html','<p>Опишите команды для создания виртуального окружения и установки FastAPI с Uvicorn.</p>'
            ),
            jsonb_build_object(
                'title','Первый запуск',
                'html','<p>Сформулируйте шаги запуска простого приложения FastAPI.</p>'
            )
        ),
        'images', jsonb_build_array('lesson-images/fastapi-logo.png')
    ),
    jsonb_build_object('duration','10m')
),
(
    (select id from sec where number = 1),
    2,
    'Создание первого приложения',
    'sozdanie-pervogo-prilozheniya',
    'published',
    jsonb_build_object(
        'theory', jsonb_build_object(
            'title', 'Первый эндпоинт',
            'html', '<p>Минимальное приложение FastAPI состоит из объекта <code>FastAPI()</code> и функции-обработчика.</p><pre><code class="language-python">from fastapi import FastAPI\napp = FastAPI()\n\n@app.get("/")\ndef root():\n    return {"message": "Hello FastAPI"}</code></pre>',
            'images', jsonb_build_array('lesson-images/first-endpoint.png')
        ),
        'tests', jsonb_build_array(
            jsonb_build_object(
                'question','Как создаётся приложение FastAPI?',
                'options', jsonb_build_array('FastAPI.new()','FastAPI()','createFastAPI()','fastapi()'),
                'correct_index', 1
            ),
            jsonb_build_object(
                'question','Какой декоратор используется для GET?',
                'options', jsonb_build_array('@app.get','@app.post','@app.route','@app.fetch'),
                'correct_index', 0
            ),
            jsonb_build_object(
                'question','Что возвращает обработчик?',
                'options', jsonb_build_array('Только строку','Словарь/JSON','HTML-файл','SQL-таблицу'),
                'correct_index', 1
            ),
            jsonb_build_object(
                'question','Какой сервер обычно используют с FastAPI?',
                'options', jsonb_build_array('Gunicorn','Uvicorn','Apache','IIS'),
                'correct_index', 1
            )
        ),
        'tasks', jsonb_build_array(
            jsonb_build_object(
                'title','Приветствие',
                'html','<p>Напишите эндпоинт /hello, который возвращает JSON с полем greeting.</p>'
            ),
            jsonb_build_object(
                'title','Параметры',
                'html','<p>Опишите, как передать параметр name в GET-запросе.</p>'
            )
        ),
        'images', jsonb_build_array('lesson-images/first-endpoint.png')
    ),
    jsonb_build_object('duration','15m')
),
(
    (select id from sec where number = 2),
    1,
    'Маршруты и параметры',
    'marshruty-i-parametry',
    'published',
    jsonb_build_object(
        'theory', jsonb_build_object(
            'title', 'Параметры пути и запросов',
            'html', '<p>FastAPI поддерживает параметры пути и параметры запроса.</p><pre><code class="language-python">@app.get("/items/{item_id}")\ndef get_item(item_id: int, q: str | None = None):\n    return {"item_id": item_id, "q": q}</code></pre>',
            'images', jsonb_build_array('lesson-images/path-params.png')
        ),
        'tests', jsonb_build_array(
            jsonb_build_object(
                'question','Где определяется параметр пути?',
                'options', jsonb_build_array('В теле запроса','В URL','В заголовках','В cookies'),
                'correct_index', 1
            ),
            jsonb_build_object(
                'question','Как задать необязательный параметр запроса?',
                'options', jsonb_build_array('q: str','q: str | None = None','q = required','q: optional'),
                'correct_index', 1
            ),
            jsonb_build_object(
                'question','Типизация параметров используется для:',
                'options', jsonb_build_array('Скрытия ошибок','Автодокументации и валидации','Сжатия данных','Кеширования'),
                'correct_index', 1
            ),
            jsonb_build_object(
                'question','Параметры запроса идут после:',
                'options', jsonb_build_array('Слеша','Знака ?','Хэша','Двоеточия'),
                'correct_index', 1
            )
        ),
        'tasks', jsonb_build_array(
            jsonb_build_object(
                'title','Параметр item_id',
                'html','<p>Создайте маршрут /items/{item_id} и опишите, как передать item_id.</p>'
            ),
            jsonb_build_object(
                'title','Необязательный q',
                'html','<p>Добавьте необязательный параметр q и опишите его использование.</p>'
            )
        ),
        'images', jsonb_build_array('lesson-images/path-params.png')
    ),
    jsonb_build_object('duration','20m')
),
(
    (select id from sec where number = 2),
    2,
    'Ответы и модели',
    'otvety-i-modeli',
    'published',
    jsonb_build_object(
        'theory', jsonb_build_object(
            'title', 'Ответы и Pydantic',
            'html', '<p>FastAPI использует Pydantic для валидации данных.</p><pre><code class="language-python">from pydantic import BaseModel\n\nclass Item(BaseModel):\n    name: str\n    price: float</code></pre>',
            'images', jsonb_build_array('lesson-images/pydantic-model.png')
        ),
        'tests', jsonb_build_array(
            jsonb_build_object(
                'question','Какая библиотека отвечает за валидацию?',
                'options', jsonb_build_array('SQLAlchemy','Pydantic','Marshmallow','Celery'),
                'correct_index', 1
            ),
            jsonb_build_object(
                'question','Что описывает BaseModel?',
                'options', jsonb_build_array('Шаблон HTML','Схему данных','Docker-образ','Системный сервис'),
                'correct_index', 1
            ),
            jsonb_build_object(
                'question','Типы полей нужны для:',
                'options', jsonb_build_array('Валидации и документации','Шифрования','Архивации','Рендеринга CSS'),
                'correct_index', 0
            ),
            jsonb_build_object(
                'question','FastAPI возвращает по умолчанию:',
                'options', jsonb_build_array('XML','JSON','CSV','PDF'),
                'correct_index', 1
            )
        ),
        'tasks', jsonb_build_array(
            jsonb_build_object(
                'title','Модель Item',
                'html','<p>Опишите модель Item с полями name и price.</p>'
            ),
            jsonb_build_object(
                'title','Ответ с моделью',
                'html','<p>Опишите, как вернуть объект Item из эндпоинта.</p>'
            )
        ),
        'images', jsonb_build_array('lesson-images/pydantic-model.png')
    ),
    jsonb_build_object('duration','20m')
);
