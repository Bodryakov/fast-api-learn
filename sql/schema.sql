-- Назначение файла:
-- Этот скрипт создаёт структуру базы данных для проекта Fast-API-Learn в Supabase.
-- Включает таблицы разделов и уроков, связи, индексы и ограничения уникальности.

-- Включаем расширение для UUID (на случай использования в будущем).
create extension if not exists "uuid-ossp";

-- Таблица разделов.
create table if not exists public.sections (
    -- Уникальный идентификатор раздела.
    id uuid primary key default uuid_generate_v4(),
    -- Порядковый номер раздела (уникален).
    number integer not null unique,
    -- Заголовок раздела.
    title text not null,
    -- ЧПУ-идентификатор раздела (уникален).
    slug text not null unique,
    -- Дополнительные метаданные (на будущее).
    meta jsonb not null default '{}'::jsonb,
    -- Даты создания и обновления.
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Ограничение формата slug для разделов: только строчные латинские буквы и дефисы.
alter table public.sections
    add constraint sections_slug_format
    check (slug ~ '^[a-z]+(-[a-z]+)*$');

-- Таблица уроков.
create table if not exists public.lessons (
    -- Уникальный идентификатор урока.
    id uuid primary key default uuid_generate_v4(),
    -- Внешний ключ на раздел.
    section_id uuid not null references public.sections(id) on delete cascade,
    -- Порядковый номер урока в рамках раздела.
    number integer not null,
    -- Заголовок урока.
    title text not null,
    -- ЧПУ-идентификатор урока.
    slug text not null,
    -- Статус публикации: draft или published.
    status text not null default 'draft',
    -- Основной контент урока в JSONB: теория, тесты, задачи, изображения.
    content jsonb not null default '{}'::jsonb,
    -- Дополнительные метаданные.
    meta jsonb not null default '{}'::jsonb,
    -- Даты создания и обновления.
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    -- Уникальность номера и slug внутри раздела.
    unique (section_id, number),
    unique (section_id, slug)
);

-- Ограничение формата slug для уроков: только строчные латинские буквы и дефисы.
alter table public.lessons
    add constraint lessons_slug_format
    check (slug ~ '^[a-z]+(-[a-z]+)*$');

-- Ограничение допустимых значений статуса публикации.
alter table public.lessons
    add constraint lessons_status_enum
    check (status in ('draft', 'published'));

-- Индекс для ускорения выборки опубликованных уроков.
create index if not exists lessons_status_idx on public.lessons(status);

-- Индекс для ускорения выборки уроков по разделу.
create index if not exists lessons_section_idx on public.lessons(section_id);

-- Триггер для автоматического обновления updated_at.
create or replace function public.set_updated_at()
returns trigger as $$
begin
    -- Обновляем поле updated_at на текущее время.
    new.updated_at := now();
    return new;
end;
$$ language plpgsql;

-- Триггер для таблицы sections.
create trigger trg_sections_updated
before update on public.sections
for each row
execute function public.set_updated_at();

-- Триггер для таблицы lessons.
create trigger trg_lessons_updated
before update on public.lessons
for each row
execute function public.set_updated_at();
