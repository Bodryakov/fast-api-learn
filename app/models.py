# Назначение файла:
# Pydantic-схемы для валидации и сериализации данных.

# Импортируем типы данных.
from typing import List, Optional

# Импортируем базовый класс моделей Pydantic.
from pydantic import BaseModel, Field

# Схема тестового вопроса.
class TestQuestion(BaseModel):
    # Текст вопроса.
    question: str
    # Варианты ответов (4 варианта).
    options: List[str] = Field(..., min_length=4, max_length=4)
    # Индекс правильного ответа (0-3).
    correct_index: int = Field(..., ge=0, le=3)

# Схема задачи.
class TaskItem(BaseModel):
    # Заголовок задачи.
    title: str
    # Текст/HTML задачи.
    html: str

# Схема теоретической части.
class TheoryBlock(BaseModel):
    # Заголовок блока.
    title: str
    # HTML-содержимое.
    html: str
    # Пути изображений.
    images: Optional[List[str]] = []

# Полный контент урока.
class LessonContent(BaseModel):
    # Теоретический блок.
    theory: TheoryBlock
    # Список тестов.
    tests: List[TestQuestion]
    # Список задач.
    tasks: List[TaskItem]
    # Глобальный список путей изображений.
    images: Optional[List[str]] = []

# Схема раздела.
class SectionIn(BaseModel):
    # Порядковый номер.
    number: int
    # Заголовок.
    title: str
    # Slug.
    slug: str

# Схема урока.
class LessonIn(BaseModel):
    # Идентификатор раздела.
    section_id: str
    # Порядковый номер урока.
    number: int
    # Заголовок урока.
    title: str
    # Slug урока.
    slug: str
    # Статус.
    status: str
    # Контент урока.
    content: LessonContent
