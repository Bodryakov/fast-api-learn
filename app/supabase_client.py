# Назначение файла:
# Подключение к Supabase и функции доступа к данным и Storage.

# Импортируем системные инструменты.
import os
import re
import uuid

# Импортируем клиент Supabase.
from supabase import create_client

# Импортируем загрузчик переменных окружения.
from dotenv import load_dotenv

# Импортируем тип для файлов.
from typing import List, Dict, Any

# Загружаем переменные окружения из .env (если файл существует).
load_dotenv()

# Переменные окружения для Supabase.
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
STORAGE_BUCKET = os.getenv('STORAGE_BUCKET', 'lesson-images')

# Инициализируем клиента Supabase.
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Регулярное выражение для извлечения data-path изображений.
IMAGE_PATH_RE = re.compile(r'data-path="([^"]+)"')

# Получаем все разделы.
def get_sections() -> List[Dict[str, Any]]:
    # Запрашиваем разделы, отсортированные по номеру.
    response = supabase.table('sections').select('*').order('number').execute()
    return response.data or []

# Получаем все уроки.
def get_lessons() -> List[Dict[str, Any]]:
    # Запрашиваем уроки, отсортированные по номеру внутри раздела.
    response = supabase.table('lessons').select('*').order('number').execute()
    return response.data or []

# Получаем урок по id.
def get_lesson_by_id(lesson_id: str) -> Dict[str, Any] | None:
    # Фильтруем по id.
    response = supabase.table('lessons').select('*').eq('id', lesson_id).limit(1).execute()
    data = response.data or []
    return data[0] if data else None

# Получаем раздел по номеру и slug.
def get_section_by_number_slug(number: int, slug: str) -> Dict[str, Any] | None:
    # Фильтруем по номеру и slug.
    response = (
        supabase.table('sections')
        .select('*')
        .eq('number', number)
        .eq('slug', slug)
        .limit(1)
        .execute()
    )
    data = response.data or []
    return data[0] if data else None

# Получаем раздел по id.
def get_section_by_id(section_id: str) -> Dict[str, Any] | None:
    # Фильтруем по id.
    response = supabase.table('sections').select('*').eq('id', section_id).limit(1).execute()
    data = response.data or []
    return data[0] if data else None

# Получаем урок по разделу и slug.
def get_lesson_by_section(number: int, section_id: str, lesson_slug: str, lesson_number: int) -> Dict[str, Any] | None:
    # Фильтруем по разделу, номеру и slug.
    response = (
        supabase.table('lessons')
        .select('*')
        .eq('section_id', section_id)
        .eq('number', lesson_number)
        .eq('slug', lesson_slug)
        .limit(1)
        .execute()
    )
    data = response.data or []
    return data[0] if data else None

# Создаём раздел.
def create_section(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Добавляем запись.
    response = supabase.table('sections').insert(payload).execute()
    return response.data[0]

# Обновляем раздел.
def update_section(section_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    # Обновляем запись по id.
    response = supabase.table('sections').update(payload).eq('id', section_id).execute()
    return response.data[0]

# Удаляем раздел.
def delete_section(section_id: str) -> None:
    # Удаляем раздел (уроки удалятся каскадно).
    supabase.table('sections').delete().eq('id', section_id).execute()

# Создаём урок.
def create_lesson(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Добавляем запись.
    response = supabase.table('lessons').insert(payload).execute()
    return response.data[0]

# Обновляем урок.
def update_lesson(lesson_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    # Обновляем запись.
    response = supabase.table('lessons').update(payload).eq('id', lesson_id).execute()
    return response.data[0]

# Удаляем урок и связанные изображения.
def delete_lesson(lesson_id: str) -> None:
    # Сначала получаем урок, чтобы извлечь пути изображений.
    response = supabase.table('lessons').select('content').eq('id', lesson_id).limit(1).execute()
    data = response.data or []
    if data:
        content = data[0].get('content') or {}
        image_paths = content.get('images') or []
        if image_paths:
            # Удаляем изображения из Storage.
            supabase.storage.from_(STORAGE_BUCKET).remove(image_paths)
    # Удаляем сам урок.
    supabase.table('lessons').delete().eq('id', lesson_id).execute()

# Загружаем изображение в Storage.
def upload_image(file_bytes: bytes, filename: str, content_type: str) -> Dict[str, str]:
    # Генерируем уникальный путь.
    ext = os.path.splitext(filename)[1].lower() or '.png'
    unique_name = f"{uuid.uuid4().hex}{ext}"
    # Загружаем файл в бакет.
    supabase.storage.from_(STORAGE_BUCKET).upload(
        unique_name,
        file_bytes,
        {"content-type": content_type, "x-upsert": "true"},
    )
    # Получаем публичный URL.
    public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(unique_name)
    return {"path": unique_name, "url": public_url}

# Извлекаем пути изображений из HTML.
def extract_image_paths(html: str) -> List[str]:
    # Ищем data-path, выставленный при вставке изображения.
    return IMAGE_PATH_RE.findall(html or '')
