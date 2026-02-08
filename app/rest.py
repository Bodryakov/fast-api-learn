# Назначение файла:
# REST API для CRUD-операций с разделами и уроками, загрузки изображений и валидации.

# Импортируем системные инструменты.
import re

# Импортируем FastAPI компоненты.
from fastapi import APIRouter, Request, UploadFile, File, HTTPException
# Импортируем ответы JSON.
from fastapi.responses import JSONResponse

# Импортируем библиотеку для очистки HTML.
import bleach

# Импортируем модели для валидации.
from app.models import SectionIn, LessonIn
# Импортируем функции Supabase.
from app.supabase_client import (
    get_sections,
    get_lessons,
    get_lesson_by_id,
    create_section,
    update_section,
    delete_section,
    create_lesson,
    update_lesson,
    delete_lesson,
    upload_image,
    extract_image_paths,
)
# Импортируем функции безопасности.
from app.admin_auth import require_admin, verify_csrf_token

# Создаём роутер API.
api_router = APIRouter(prefix='/api')

# Регулярное выражение для slug.
SLUG_RE = re.compile(r'^[a-z]+(-[a-z]+)*$')

# Настройки очистки HTML от XSS.
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's', 'span',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote',
    'pre', 'code',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'a', 'img',
]
ALLOWED_ATTRS = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'data-path'],
    'span': ['style'],
    'p': ['style'],
    'code': ['class'],
    'pre': ['class'],
    'table': ['class'],
}
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

# Очистка HTML.
def sanitize_html(html: str) -> str:
    # Очищаем HTML, удаляя опасные теги/атрибуты.
    return bleach.clean(
        html or '',
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )

# Проверяем валидность slug.
def validate_slug(slug: str) -> None:
    # Проверяем регулярное выражение.
    if not SLUG_RE.match(slug or ''):
        raise HTTPException(status_code=400, detail='Slug должен содержать только строчные буквы и дефисы.')

# Проверяем CSRF для опасных методов.
def ensure_csrf(request: Request):
    # Достаём токен из заголовка.
    token = request.headers.get('X-CSRF-Token')
    if not token:
        raise HTTPException(status_code=403, detail='CSRF token missing')
    verify_csrf_token(request, token)

# Создание раздела.
@api_router.post('/sections')
async def api_create_section(request: Request, payload: SectionIn):
    # Проверяем админ-доступ.
    require_admin(request)
    # Проверяем CSRF.
    ensure_csrf(request)
    # Валидируем slug.
    validate_slug(payload.slug)

    # Создаём раздел.
    created = create_section(payload.model_dump())
    return JSONResponse(created)

# Обновление раздела.
@api_router.put('/sections/{section_id}')
async def api_update_section(request: Request, section_id: str, payload: SectionIn):
    # Проверяем админ-доступ.
    require_admin(request)
    # Проверяем CSRF.
    ensure_csrf(request)
    # Валидируем slug.
    validate_slug(payload.slug)

    # Обновляем раздел.
    updated = update_section(section_id, payload.model_dump())
    return JSONResponse(updated)

# Удаление раздела.
@api_router.delete('/sections/{section_id}')
async def api_delete_section(request: Request, section_id: str):
    # Проверяем админ-доступ.
    require_admin(request)
    # Проверяем CSRF.
    ensure_csrf(request)

    # Удаляем раздел.
    delete_section(section_id)
    return JSONResponse({'status': 'ok'})

# Создание урока.
@api_router.post('/lessons')
async def api_create_lesson(request: Request, payload: LessonIn):
    # Проверяем админ-доступ.
    require_admin(request)
    # Проверяем CSRF.
    ensure_csrf(request)
    # Валидируем slug.
    validate_slug(payload.slug)

    # Собираем пути изображений из HTML.
    content = payload.content.model_dump()
    theory_html = sanitize_html(content.get('theory', {}).get('html', ''))
    tasks = content.get('tasks') or []
    task_html = ' '.join([sanitize_html(t.get('html', '')) for t in tasks])
    image_paths = list(set(extract_image_paths(theory_html) + extract_image_paths(task_html)))
    content['images'] = image_paths
    if content.get('theory'):
        content['theory']['images'] = extract_image_paths(theory_html)
        content['theory']['html'] = theory_html

    # Перезаписываем очищенные HTML задач.
    for task in content.get('tasks') or []:
        task['html'] = sanitize_html(task.get('html', ''))

    # Создаём урок.
    created = create_lesson({
        'section_id': payload.section_id,
        'number': payload.number,
        'title': payload.title,
        'slug': payload.slug,
        'status': payload.status,
        'content': content,
    })
    return JSONResponse(created)

# Обновление урока.
@api_router.put('/lessons/{lesson_id}')
async def api_update_lesson(request: Request, lesson_id: str, payload: LessonIn):
    # Проверяем админ-доступ.
    require_admin(request)
    # Проверяем CSRF.
    ensure_csrf(request)
    # Валидируем slug.
    validate_slug(payload.slug)

    # Собираем пути изображений из HTML.
    content = payload.content.model_dump()
    theory_html = sanitize_html(content.get('theory', {}).get('html', ''))
    tasks = content.get('tasks') or []
    task_html = ' '.join([sanitize_html(t.get('html', '')) for t in tasks])
    image_paths = list(set(extract_image_paths(theory_html) + extract_image_paths(task_html)))
    content['images'] = image_paths
    if content.get('theory'):
        content['theory']['images'] = extract_image_paths(theory_html)
        content['theory']['html'] = theory_html

    # Перезаписываем очищенные HTML задач.
    for task in content.get('tasks') or []:
        task['html'] = sanitize_html(task.get('html', ''))

    # Обновляем урок.
    updated = update_lesson(lesson_id, {
        'section_id': payload.section_id,
        'number': payload.number,
        'title': payload.title,
        'slug': payload.slug,
        'status': payload.status,
        'content': content,
    })
    return JSONResponse(updated)

# Удаление урока.
@api_router.delete('/lessons/{lesson_id}')
async def api_delete_lesson(request: Request, lesson_id: str):
    # Проверяем админ-доступ.
    require_admin(request)
    # Проверяем CSRF.
    ensure_csrf(request)

    # Удаляем урок и изображения.
    delete_lesson(lesson_id)
    return JSONResponse({'status': 'ok'})

# Загрузка изображений.
@api_router.post('/upload-image')
async def api_upload_image(request: Request, file: UploadFile = File(...)):
    # Проверяем админ-доступ.
    require_admin(request)
    # Проверяем CSRF.
    ensure_csrf(request)

    # Проверяем размер файла (<= 5 МБ).
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail='Файл больше 5 МБ.')

    # Загружаем файл в Storage.
    result = upload_image(content, file.filename, file.content_type or 'image/png')
    return JSONResponse(result)
# Получение списка разделов.
@api_router.get('/sections')
async def api_list_sections(request: Request):
    # Проверяем админ-доступ.
    require_admin(request)
    # Возвращаем список разделов.
    return JSONResponse(get_sections())

# Получение списка уроков.
@api_router.get('/lessons')
async def api_list_lessons(request: Request, section_id: str | None = None):
    # Проверяем админ-доступ.
    require_admin(request)
    # Фильтруем по разделу при необходимости.
    lessons = get_lessons()
    if section_id:
        lessons = [l for l in lessons if l.get('section_id') == section_id]
    return JSONResponse(lessons)

# Получение урока по id.
@api_router.get('/lessons/{lesson_id}')
async def api_get_lesson(request: Request, lesson_id: str):
    # Проверяем админ-доступ.
    require_admin(request)
    lesson = get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail='Lesson not found')
    return JSONResponse(lesson)
