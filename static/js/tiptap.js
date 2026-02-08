// Назначение файла: инициализация Tiptap, панели инструментов и загрузка изображений.

// Импортируем базовые компоненты Tiptap.
import { Editor } from 'https://esm.sh/@tiptap/core';
import StarterKit from 'https://esm.sh/@tiptap/starter-kit';
import Underline from 'https://esm.sh/@tiptap/extension-underline';
import Link from 'https://esm.sh/@tiptap/extension-link';
import Image from 'https://esm.sh/@tiptap/extension-image';
import { TextStyle } from 'https://esm.sh/@tiptap/extension-text-style';
import { Color } from 'https://esm.sh/@tiptap/extension-color';
import { FontFamily } from 'https://esm.sh/@tiptap/extension-font-family';
import { Table } from 'https://esm.sh/@tiptap/extension-table';
import TableRow from 'https://esm.sh/@tiptap/extension-table-row';
import TableHeader from 'https://esm.sh/@tiptap/extension-table-header';
import TableCell from 'https://esm.sh/@tiptap/extension-table-cell';

// Расширяем Image, чтобы хранить data-path.
const CustomImage = Image.extend({
    addAttributes() {
        return {
            ...this.parent?.(),
            'data-path': { default: null },
            'alt': { default: null },
        };
    },
});

// Получаем CSRF-токен.
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';

// Загрузка изображения в backend.
async function uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/api/upload-image', {
        method: 'POST',
        headers: { 'X-CSRF-Token': csrfToken },
        body: formData,
    });

    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || 'Ошибка загрузки изображения');
    }

    return response.json();
}

function resolveElement(target) {
    if (typeof target === 'string') {
        return document.getElementById(target);
    }
    return target instanceof HTMLElement ? target : null;
}

// Создаём редактор.
function createEditor(target) {
    const element = resolveElement(target);
    if (!element) {
        throw new Error('Tiptap target не найден.');
    }
    return new Editor({
        element,
        extensions: [
            StarterKit,
            Underline,
            Link.configure({ openOnClick: false }),
            TextStyle,
            Color,
            FontFamily,
            Table.configure({ resizable: true }),
            TableRow,
            TableHeader,
            TableCell,
            CustomImage,
        ],
        content: '',
    });
}

// Создаём тулбар.
function createToolbar(toolbarTarget, editor) {
    const toolbar = resolveElement(toolbarTarget);
    if (!toolbar) return;

    const buttons = [
        { label: 'B', action: () => editor.chain().focus().toggleBold().run() },
        { label: 'I', action: () => editor.chain().focus().toggleItalic().run() },
        { label: 'U', action: () => editor.chain().focus().toggleUnderline().run() },
        { label: 'H2', action: () => editor.chain().focus().toggleHeading({ level: 2 }).run() },
        { label: '•', action: () => editor.chain().focus().toggleBulletList().run() },
        { label: '1.', action: () => editor.chain().focus().toggleOrderedList().run() },
        { label: '</>', action: () => insertCodeBlock(editor, 'python') },
        { label: 'Table', action: () => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run() },
        { label: 'Link', action: () => setLink(editor) },
        { label: 'Img', action: () => insertImage(editor) },
    ];

    buttons.forEach((btn) => {
        const b = document.createElement('button');
        b.type = 'button';
        b.textContent = btn.label;
        b.addEventListener('click', btn.action);
        toolbar.appendChild(b);
    });

    // Цвет текста.
    const colorInput = document.createElement('input');
    colorInput.type = 'color';
    colorInput.addEventListener('input', (e) => {
        editor.chain().focus().setColor(e.target.value).run();
    });
    toolbar.appendChild(colorInput);

    // Выбор шрифта.
    const fontSelect = document.createElement('select');
    ['Manrope', 'Arial', 'Georgia', 'Courier New'].forEach((f) => {
        const opt = document.createElement('option');
        opt.value = f;
        opt.textContent = f;
        fontSelect.appendChild(opt);
    });
    fontSelect.addEventListener('change', (e) => {
        editor.chain().focus().setFontFamily(e.target.value).run();
    });
    toolbar.appendChild(fontSelect);

    // Размер шрифта.
    const sizeSelect = document.createElement('select');
    ['12px', '14px', '16px', '18px', '20px', '24px'].forEach((s) => {
        const opt = document.createElement('option');
        opt.value = s;
        opt.textContent = s;
        sizeSelect.appendChild(opt);
    });
    sizeSelect.addEventListener('change', (e) => {
        editor.chain().focus().setMark('textStyle', { style: `font-size: ${e.target.value};` }).run();
    });
    toolbar.appendChild(sizeSelect);

    // Быстрые вставки кода по языкам.
    const langSelect = document.createElement('select');
    ['python', 'fastapi', 'html', 'css', 'js'].forEach((l) => {
        const opt = document.createElement('option');
        opt.value = l;
        opt.textContent = l;
        langSelect.appendChild(opt);
    });
    const codeBtn = document.createElement('button');
    codeBtn.type = 'button';
    codeBtn.textContent = 'Код';
    codeBtn.addEventListener('click', () => insertCodeBlock(editor, langSelect.value));
    toolbar.appendChild(langSelect);
    toolbar.appendChild(codeBtn);
}

function createRichEditor({ toolbarEl, editorEl }) {
    const editor = createEditor(editorEl);
    createToolbar(toolbarEl, editor);
    return editor;
}

// Вставка ссылки.
function setLink(editor) {
    const url = prompt('Введите URL');
    if (!url) return;
    editor.chain().focus().extendMarkRange('link').setLink({ href: url, target: '_blank', rel: 'noopener' }).run();
}

// Вставка блока кода.
function insertCodeBlock(editor, lang) {
    const className = lang === 'fastapi' ? 'language-python' : `language-${lang}`;
    const snippet = `<pre><code class="${className}"># код</code></pre>`;
    editor.chain().focus().insertContent(snippet).run();
}

// Вставка изображения через загрузку.
async function insertImage(editor) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/png,image/jpeg,image/webp,image/svg+xml';

    input.onchange = async () => {
        const file = input.files?.[0];
        if (!file) return;
        if (file.size > 5 * 1024 * 1024) {
            alert('Файл больше 5 МБ');
            return;
        }
        const result = await uploadImage(file);
        editor.chain().focus().setImage({ src: result.url, 'data-path': result.path, alt: '' }).run();
    };

    input.click();
}

// Инициализация редакторов.
const theoryEditor = createRichEditor({
    toolbarEl: 'theoryToolbar',
    editorEl: 'theoryEditor',
});
const tasksEditor = createRichEditor({
    toolbarEl: 'tasksToolbar',
    editorEl: 'tasksEditor',
});

// Экспортируем редакторы в глобальное пространство.
function registerTestEditor(editor) {
    if (!window.tiptapEditors) {
        window.tiptapEditors = { theory: null, tasks: null, tests: [] };
    }
    window.tiptapEditors.tests = window.tiptapEditors.tests || [];
    window.tiptapEditors.tests.push(editor);
}

function unregisterTestEditor(editor) {
    if (!window.tiptapEditors) return;
    window.tiptapEditors.tests = (window.tiptapEditors.tests || []).filter((e) => e !== editor);
}

window.tiptapEditors = {
    theory: theoryEditor,
    tasks: tasksEditor,
    tests: [],
};
window.tiptapHelpers = {
    createRichEditor,
    registerTestEditor,
    unregisterTestEditor,
};

// Сигнализируем о готовности.
window.dispatchEvent(new CustomEvent('tiptap-ready'));
