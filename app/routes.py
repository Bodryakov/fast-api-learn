# Назначение файла:
# Маршруты серверного рендеринга страниц сайта и админ-панели.

# Импортируем FastAPI компоненты.
import json
import re

from fastapi import APIRouter, Request, Form, HTTPException
# Импортируем ответы и перенаправления.
from fastapi.responses import RedirectResponse
# Импортируем шаблоны Jinja2.
from fastapi.templating import Jinja2Templates

# Импортируем функции работы с Supabase.
from app.supabase_client import (
    get_sections,
    get_lessons,
    get_section_by_number_slug,
    get_lesson_by_section,
    get_section_by_id,
    get_lesson_by_id,
    create_section,
    update_section,
    delete_section,
    create_lesson,
    update_lesson,
    delete_lesson,
    extract_image_paths,
)
# Импортируем функции аутентификации.
from app.admin_auth import verify_credentials, set_admin_session, clear_admin_session, ensure_csrf_token
# Импортируем очистку HTML и проверку slug.
from app.rest import sanitize_html, validate_slug

# Создаём роутер страниц.
pages_router = APIRouter()

# Регулярка для распознавания секций и уроков вида №-slug (например, 1-vvedenie-v-fastapi).
DESCRIPTOR_RE = re.compile(r'^(?P<number>\d+)-(?P<slug>[a-z]+(?:-[a-z]+)*)$')


def parse_descriptor(descriptor: str):
    match = DESCRIPTOR_RE.match(descriptor or '')
    if not match:
        return None
    return int(match.group('number')), match.group('slug')

# Нормализуем тесты из формы, очищаем HTML и приводим к 4 вариантам.
def normalize_tests(raw_tests):
    cleaned = []
    for test in (raw_tests or []):
        question_html = sanitize_html(test.get('question', '') or '')
        raw_options = test.get('options') or []
        options = [sanitize_html(opt or '') for opt in raw_options]
        if len(options) < 4:
            options += [''] * (4 - len(options))
        options = options[:4]
        try:
            correct_index = int(test.get('correct_index', 0))
        except (TypeError, ValueError):
            correct_index = 0
        correct_index = max(0, min(correct_index, 3))
        cleaned.append({
            'question': question_html,
            'options': options,
            'correct_index': correct_index,
        })
    return cleaned

# Инициализируем шаблоны.
templates = Jinja2Templates(directory='templates')

# Главная страница: список разделов и уроков.
@pages_router.get('/')
async def index(request: Request):
    # Загружаем данные разделов и уроков.
    sections = get_sections()
    lessons = [l for l in get_lessons() if l.get('status') == 'published']

    # Собираем уроки по разделам.
    lessons_by_section = {}
    for lesson in lessons:
        lessons_by_section.setdefault(lesson['section_id'], []).append(lesson)

    # Сортируем уроки внутри разделов по номеру.
    for section_id in lessons_by_section:
        lessons_by_section[section_id] = sorted(lessons_by_section[section_id], key=lambda x: x['number'])

    # Рендерим шаблон.
    return templates.TemplateResponse('index.html', {
        'request': request,
        'sections': sections,
        'lessons_by_section': lessons_by_section,
    })

# Страница раздела.
@pages_router.get('/section-{section_descriptor}')
async def section_page(request: Request, section_descriptor: str):
    parsed = parse_descriptor(section_descriptor)
    if not parsed:
        return templates.TemplateResponse('404.html', {'request': request}, status_code=404)

    section_number, section_slug = parsed
    # Ищем раздел.
    section = get_section_by_number_slug(section_number, section_slug)
    if not section:
        return templates.TemplateResponse('404.html', {'request': request}, status_code=404)

    # Загружаем уроки раздела.
    lessons = [l for l in get_lessons() if l.get('section_id') == section['id'] and l.get('status') == 'published']
    lessons = sorted(lessons, key=lambda x: x['number'])

    # Рендерим страницу раздела.
    return templates.TemplateResponse('section.html', {
        'request': request,
        'section': section,
        'lessons': lessons,
    })

@pages_router.get('/section-{section_descriptor}/lesson-{lesson_descriptor}')
async def lesson_page(request: Request, section_descriptor: str, lesson_descriptor: str):
    # Ищем раздел.
    section_parsed = parse_descriptor(section_descriptor)
    lesson_parsed = parse_descriptor(lesson_descriptor)
    if not section_parsed or not lesson_parsed:
        return templates.TemplateResponse('404.html', {'request': request}, status_code=404)
    section_number, section_slug = section_parsed
    lesson_number, lesson_slug = lesson_parsed
    section = get_section_by_number_slug(section_number, section_slug)
    if not section:
        return templates.TemplateResponse('404.html', {'request': request}, status_code=404)

    # Ищем урок.
    lesson = get_lesson_by_section(section_number, section['id'], lesson_slug, lesson_number)
    if not lesson or lesson.get('status') != 'published':
        return templates.TemplateResponse('404.html', {'request': request}, status_code=404)

    # Загружаем список уроков для навигации.
    lessons = [l for l in get_lessons() if l.get('section_id') == section['id'] and l.get('status') == 'published']
    lessons = sorted(lessons, key=lambda x: x['number'])

    # Определяем предыдущий и следующий урок.
    current_index = next((i for i, l in enumerate(lessons) if l['id'] == lesson['id']), None)
    prev_lesson = lessons[current_index - 1] if current_index is not None and current_index > 0 else None
    next_lesson = lessons[current_index + 1] if current_index is not None and current_index < len(lessons) - 1 else None

    # Рендерим страницу урока.
    return templates.TemplateResponse('lesson.html', {
        'request': request,
        'section': section,
        'lesson': lesson,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
    })

# Страница входа или админка.
@pages_router.get('/bod')
async def admin_page(request: Request):
    # Обеспечиваем CSRF-токен для форм.
    csrf_token = ensure_csrf_token(request)

    # Если админ уже авторизован — редиректим на дашборд.
    if request.session.get('is_admin'):
        return RedirectResponse('/bod/dashboard', status_code=302)

    # Иначе — показываем форму логина.
    return templates.TemplateResponse('admin_login.html', {
        'request': request,
        'csrf_token': csrf_token,
    })

# Дашборд админки.
@pages_router.get('/bod/dashboard')
async def admin_dashboard(request: Request):
    if not request.session.get('is_admin'):
        return RedirectResponse('/bod', status_code=302)

    csrf_token = ensure_csrf_token(request)

    sections = get_sections()
    lessons = get_lessons()

    lessons_by_section: dict[str, list] = {}
    for lesson in lessons:
        lessons_by_section.setdefault(lesson['section_id'], []).append(lesson)
    for section_id in lessons_by_section:
        lessons_by_section[section_id] = sorted(lessons_by_section[section_id], key=lambda x: x['number'])

    return templates.TemplateResponse('admin.html', {
        'request': request,
        'csrf_token': csrf_token,
        'sections': sections,
        'lessons_by_section': lessons_by_section,
    })

# Создание раздела.
@pages_router.get('/bod/section/create')
async def admin_section_create_page(request: Request):
    if not request.session.get('is_admin'):
        return RedirectResponse('/bod', status_code=302)
    return templates.TemplateResponse('admin_section.html', {
        'request': request,
        'csrf_token': ensure_csrf_token(request),
        'section': None,
        'error': None,
    })

@pages_router.post('/bod/section/create')
async def admin_section_create(request: Request):
    if not request.session.get('is_admin'):
        return RedirectResponse('/bod', status_code=302)

    form = await request.form()
    csrf_token = form.get('csrf_token', '')
    if csrf_token != request.session.get('csrf_token'):
        return templates.TemplateResponse('admin_section.html', {
            'request': request,
            'csrf_token': ensure_csrf_token(request),
            'section': None,
            'error': 'Неверный CSRF-токен.',
        }, status_code=403)

    try:
        title = (form.get('title') or '').strip()
        slug = (form.get('slug') or '').strip()
        number = int(form.get('number', '0'))
        if not title:
            raise ValueError('Название раздела обязательно.')
        validate_slug(slug)

        create_section({'number': number, 'title': title, 'slug': slug})
        return RedirectResponse('/bod/dashboard', status_code=302)
    except Exception as exc:
        error = exc.detail if isinstance(exc, HTTPException) else str(exc)
        return templates.TemplateResponse('admin_section.html', {
            'request': request,
            'csrf_token': ensure_csrf_token(request),
            'section': {'number': form.get('number', ''), 'title': title, 'slug': slug},
            'error': error,
        }, status_code=400)

# Редактирование раздела.
@pages_router.get('/bod/section/edit/{section_id}')
async def admin_section_edit_page(request: Request, section_id: str):
    if not request.session.get('is_admin'):
        return RedirectResponse('/bod', status_code=302)

    section = get_section_by_id(section_id)
    if not section:
        return RedirectResponse('/bod/dashboard', status_code=302)

    return templates.TemplateResponse('admin_section.html', {
        'request': request,
        'csrf_token': ensure_csrf_token(request),
        'section': section,
        'error': None,
    })

@pages_router.post('/bod/section/edit/{section_id}')
async def admin_section_edit(request: Request, section_id: str):
    if not request.session.get('is_admin'):
        return RedirectResponse('/bod', status_code=302)

    section = get_section_by_id(section_id)
    if not section:
        return RedirectResponse('/bod/dashboard', status_code=302)

    form = await request.form()
    csrf_token = form.get('csrf_token', '')
    if csrf_token != request.session.get('csrf_token'):
        return templates.TemplateResponse('admin_section.html', {
            'request': request,
            'csrf_token': ensure_csrf_token(request),
            'section': section,
            'error': 'Неверный CSRF-токен.',
        }, status_code=403)

    try:
        title = (form.get('title') or '').strip()
        slug = (form.get('slug') or '').strip()
        number = int(form.get('number', section['number']))
        if not title:
            raise ValueError('Название раздела обязательно.')
        validate_slug(slug)

        updated = update_section(section_id, {'number': number, 'title': title, 'slug': slug})
        return RedirectResponse('/bod/dashboard', status_code=302)
    except Exception as exc:
        error = exc.detail if isinstance(exc, HTTPException) else str(exc)
        return templates.TemplateResponse('admin_section.html', {
            'request': request,
            'csrf_token': ensure_csrf_token(request),
            'section': {'id': section_id, 'number': form.get('number', ''), 'title': title, 'slug': slug},
            'error': error,
        }, status_code=400)

# Удаление раздела.
@pages_router.post('/bod/section/delete/{section_id}')
async def admin_section_delete(request: Request, section_id: str, csrf_token: str = Form(...)):
    if not request.session.get('is_admin'):
        return RedirectResponse('/bod', status_code=302)

    if csrf_token != request.session.get('csrf_token'):
        return RedirectResponse('/bod/dashboard', status_code=302)

    delete_section(section_id)
    return RedirectResponse('/bod/dashboard', status_code=302)

# Создание урока.
@pages_router.get('/bod/lesson/create')
async def admin_lesson_create_page(request: Request, section_id: str | None = None):
    if not request.session.get('is_admin'):
        return RedirectResponse('/bod', status_code=302)

    sections = get_sections()
    initial_data = {'theory_html': '', 'tasks': [], 'tests': []}
    return templates.TemplateResponse('admin_lesson.html', {
        'request': request,
        'csrf_token': ensure_csrf_token(request),
        'lesson': None,
        'sections': sections,
        'default_section_id': section_id,
        'initial_data': initial_data,
        'error': None,
    })

@pages_router.post('/bod/lesson/create')
async def admin_lesson_create(request: Request):
    if not request.session.get('is_admin'):
        return RedirectResponse('/bod', status_code=302)

    form = await request.form()
    csrf_token = form.get('csrf_token', '')
    if csrf_token != request.session.get('csrf_token'):
        return RedirectResponse('/bod', status_code=302)

    try:
        section_id = form.get('section_id')
        number = int(form.get('number', '0'))
        title = (form.get('title') or '').strip()
        slug = (form.get('slug') or '').strip()
        action = form.get('action', 'draft')
        status = 'published' if action == 'publish' else 'draft'
        if not section_id:
            raise ValueError('Раздел обязателен.')
        if not title:
            raise ValueError('Название урока обязательно.')
        validate_slug(slug)

        theory_html = sanitize_html(form.get('theory_html', ''))
        tasks = json.loads(form.get('tasks_json') or '[]')
        tests = normalize_tests(json.loads(form.get('tests_json') or '[]'))

        for task in tasks:
            task['html'] = sanitize_html(task.get('html', ''))

        task_html = ' '.join([task.get('html', '') for task in tasks])
        tests_html = ' '.join([test.get('question', '') for test in tests])
        image_paths = list(set(
            extract_image_paths(theory_html)
            + extract_image_paths(task_html)
            + extract_image_paths(tests_html)
        ))

        content = {
            'theory': {'title': title, 'html': theory_html, 'images': extract_image_paths(theory_html)},
            'tests': tests,
            'tasks': tasks,
            'images': image_paths,
        }

        created = create_lesson({
            'section_id': section_id,
            'number': number,
            'title': title,
            'slug': slug,
            'status': status,
            'content': content,
        })
        if action == 'draft':
            return RedirectResponse(f"/bod/lesson/edit/{created['id']}", status_code=302)
        return RedirectResponse('/bod/dashboard', status_code=302)
    except Exception as exc:
        error = exc.detail if isinstance(exc, HTTPException) else str(exc)
        sections = get_sections()
        initial_data = {
            'theory_html': form.get('theory_html', ''),
            'tasks': json.loads(form.get('tasks_json') or '[]'),
            'tests': normalize_tests(json.loads(form.get('tests_json') or '[]')),
        }
        return templates.TemplateResponse('admin_lesson.html', {
            'request': request,
            'csrf_token': ensure_csrf_token(request),
            'lesson': None,
            'sections': sections,
            'default_section_id': form.get('section_id'),
            'initial_data': initial_data,
            'error': error,
        }, status_code=400)

# Редактирование урока.
@pages_router.get('/bod/lesson/edit/{lesson_id}')
async def admin_lesson_edit_page(request: Request, lesson_id: str):
    if not request.session.get('is_admin'):
        return RedirectResponse('/bod', status_code=302)

    lesson = get_lesson_by_id(lesson_id)
    if not lesson:
        return RedirectResponse('/bod/dashboard', status_code=302)

    sections = get_sections()
    content = lesson.get('content') or {}
    initial_data = {
        'theory_html': (content.get('theory') or {}).get('html', ''),
        'tasks': content.get('tasks') or [],
        'tests': content.get('tests') or [],
    }

    return templates.TemplateResponse('admin_lesson.html', {
        'request': request,
        'csrf_token': ensure_csrf_token(request),
        'lesson': lesson,
        'sections': sections,
        'default_section_id': lesson.get('section_id'),
        'initial_data': initial_data,
        'error': None,
    })

@pages_router.post('/bod/lesson/edit/{lesson_id}')
async def admin_lesson_edit(request: Request, lesson_id: str):
    if not request.session.get('is_admin'):
        return RedirectResponse('/bod', status_code=302)

    lesson = get_lesson_by_id(lesson_id)
    if not lesson:
        return RedirectResponse('/bod/dashboard', status_code=302)

    form = await request.form()
    csrf_token = form.get('csrf_token', '')
    if csrf_token != request.session.get('csrf_token'):
        return RedirectResponse('/bod', status_code=302)

    try:
        section_id = form.get('section_id')
        number = int(form.get('number', '0'))
        title = (form.get('title') or '').strip()
        slug = (form.get('slug') or '').strip()
        action = form.get('action', 'draft')
        status = 'published' if action == 'publish' else 'draft'
        if not section_id:
            raise ValueError('Раздел обязателен.')
        if not title:
            raise ValueError('Название урока обязательно.')
        validate_slug(slug)

        theory_html = sanitize_html(form.get('theory_html', ''))
        tasks = json.loads(form.get('tasks_json') or '[]')
        tests = normalize_tests(json.loads(form.get('tests_json') or '[]'))

        for task in tasks:
            task['html'] = sanitize_html(task.get('html', ''))

        task_html = ' '.join([task.get('html', '') for task in tasks])
        tests_html = ' '.join([test.get('question', '') for test in tests])
        image_paths = list(set(
            extract_image_paths(theory_html)
            + extract_image_paths(task_html)
            + extract_image_paths(tests_html)
        ))

        content = {
            'theory': {'title': title, 'html': theory_html, 'images': extract_image_paths(theory_html)},
            'tests': tests,
            'tasks': tasks,
            'images': image_paths,
        }

        update_lesson(lesson_id, {
            'section_id': section_id,
            'number': number,
            'title': title,
            'slug': slug,
            'status': status,
            'content': content,
        })
        if action == 'draft':
            return RedirectResponse(f'/bod/lesson/edit/{lesson_id}', status_code=302)
        return RedirectResponse('/bod/dashboard', status_code=302)
    except Exception as exc:
        error = exc.detail if isinstance(exc, HTTPException) else str(exc)
        sections = get_sections()
        initial_data = {
            'theory_html': form.get('theory_html', ''),
            'tasks': json.loads(form.get('tasks_json') or '[]'),
            'tests': normalize_tests(json.loads(form.get('tests_json') or '[]')),
        }
        return templates.TemplateResponse('admin_lesson.html', {
            'request': request,
            'csrf_token': ensure_csrf_token(request),
            'lesson': lesson,
            'sections': sections,
            'default_section_id': form.get('section_id'),
            'initial_data': initial_data,
            'error': error,
        }, status_code=400)

# Удаление урока.
@pages_router.post('/bod/lesson/delete/{lesson_id}')
async def admin_lesson_delete(request: Request, lesson_id: str, csrf_token: str = Form(...)):
    if not request.session.get('is_admin'):
        return RedirectResponse('/bod', status_code=302)

    if csrf_token != request.session.get('csrf_token'):
        return RedirectResponse('/bod/dashboard', status_code=302)

    delete_lesson(lesson_id)
    return RedirectResponse('/bod/dashboard', status_code=302)

# Обработка входа.
@pages_router.post('/bod/login')
async def admin_login(request: Request, login: str = Form(...), password: str = Form(...), csrf_token: str = Form(...)):
    # Проверяем CSRF.
    if csrf_token != request.session.get('csrf_token'):
        return templates.TemplateResponse('admin_login.html', {
            'request': request,
            'csrf_token': ensure_csrf_token(request),
            'error': 'Неверный CSRF-токен.'
        }, status_code=403)

    # Проверяем логин/пароль.
    if verify_credentials(login, password):
        set_admin_session(request)
        return RedirectResponse('/bod/dashboard', status_code=302)

    # Если ошибка — возвращаем страницу с сообщением.
    return templates.TemplateResponse('admin_login.html', {
        'request': request,
        'csrf_token': ensure_csrf_token(request),
        'error': 'Неверный логин или пароль.'
    }, status_code=401)

# Выход из админки.
@pages_router.post('/bod/logout')
async def admin_logout(request: Request, csrf_token: str = Form(...)):
    # Проверяем CSRF.
    if csrf_token != request.session.get('csrf_token'):
        return RedirectResponse('/bod', status_code=302)

    # Очищаем сессию.
    clear_admin_session(request)
    return RedirectResponse('/bod', status_code=302)
