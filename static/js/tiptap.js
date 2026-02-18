// Назначение файла: инициализация Tiptap, панелей инструментов и загрузка изображений.

// Импортируем базовые компоненты Tiptap с улучшенной обработкой ошибок.
const loadTiptapModules = async () => {
    try {
        const modules = await Promise.all([
            import('https://esm.sh/@tiptap/core@2.1.0'),
            import('https://esm.sh/@tiptap/starter-kit@2.1.0'),
            import('https://esm.sh/@tiptap/extension-underline@2.1.0'),
            import('https://esm.sh/@tiptap/extension-link@2.1.0'),
            import('https://esm.sh/@tiptap/extension-image@2.1.0'),
            import('https://esm.sh/@tiptap/extension-text-style@2.1.0'),
            import('https://esm.sh/@tiptap/extension-color@2.1.0'),
            import('https://esm.sh/@tiptap/extension-font-family@2.1.0'),
            import('https://esm.sh/@tiptap/extension-table@2.1.0'),
            import('https://esm.sh/@tiptap/extension-table-row@2.1.0'),
            import('https://esm.sh/@tiptap/extension-table-header@2.1.0'),
            import('https://esm.sh/@tiptap/extension-table-cell@2.1.0')
        ]);

        return {
            Editor: modules[0].Editor,
            StarterKit: modules[1].default,
            Underline: modules[2].default,
            Link: modules[3].default,
            Image: modules[4].default,
            TextStyle: modules[5].TextStyle,
            Color: modules[6].default,
            FontFamily: modules[7].default,
            Table: modules[8].Table,
            TableRow: modules[9].default,
            TableHeader: modules[10].default,
            TableCell: modules[11].default
        };
    } catch (error) {
        console.error('Ошибка загрузки модулей Tiptap:', error);
        throw new Error('Не удалось загрузить редактор Tiptap. Проверьте подключение к интернету.');
    }
};

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

// Основная инициализация в асинхронном блоке.
(async () => {
    const {
        Editor,
        StarterKit,
        Underline,
        Link,
        Image,
        TextStyle,
        Color,
        FontFamily,
        Table,
        TableRow,
        TableHeader,
        TableCell,
    } = await loadTiptapModules();

    const CustomImage = Image.extend({
        addAttributes() {
            return {
                ...this.parent?.(),
                'data-path': { default: null },
                'alt': { default: null },
            };
        },
    });

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

    function createToolbar(toolbarTarget, editor) {
        const toolbar = resolveElement(toolbarTarget);
        if (!toolbar) return;

        const buttons = [
            { label: 'B', action: () => editor.chain().focus().toggleBold().run() },
            { label: 'I', action: () => editor.chain().focus().toggleItalic().run() },
            { label: '</>', action: () => editor.chain().focus().toggleCode().run() },
            {
                label: 'Блок кода',
                action: () => {
                    if (editor.isActive('codeBlock')) {
                        editor.chain().focus().toggleCodeBlock().run();
                    } else {
                        const { from, to } = editor.state.selection;
                        const text = editor.state.doc.textBetween(from, to, '\n');
                        editor.chain().focus().insertContent({
                            type: 'codeBlock',
                            content: [
                                {
                                    type: 'text',
                                    text: text || ' ',
                                },
                            ],
                        }).run();
                    }
                }
            },
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

        const colorInput = document.createElement('input');
        colorInput.type = 'color';
        colorInput.addEventListener('input', (e) => {
            editor.chain().focus().setColor(e.target.value).run();
        });
        toolbar.appendChild(colorInput);

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

    }

    function createRichEditor({ toolbarEl, editorEl }) {
        if (!resolveElement(editorEl)) {
            console.warn(`Tiptap target skipped: ${editorEl}`);
            return null;
        }
        const editor = createEditor(editorEl);
        createToolbar(toolbarEl, editor);
        const host = resolveElement(editorEl);
        const injectButtons = () => {
            const root = host?.querySelector('.ProseMirror') || host;
            if (!root) return;
            const blocks = root.querySelectorAll('pre');
            blocks.forEach((pre) => {
                if (pre.dataset.copyInit) return;
                pre.dataset.copyInit = '1';

                // Обернем pre в контейнер, если нужно, но Tiptap не любит лишние обертки.
                // Просто убедимся, что pre имеет position: relative
                pre.style.position = 'relative';

                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'code-copy-btn';
                btn.title = 'Скопировать';
                btn.setAttribute('contenteditable', 'false');

                const ic = document.createElement('span');
                ic.className = 'material-symbols-rounded';
                ic.textContent = 'content_copy';
                btn.appendChild(ic);

                btn.addEventListener('mousedown', (e) => e.stopPropagation());
                btn.addEventListener('click', async (e) => {
                    e.preventDefault();
                    e.stopPropagation();

                    const codeEl = pre.querySelector('code');
                    const text = codeEl ? codeEl.textContent || '' : pre.textContent || '';

                    try {
                        await navigator.clipboard?.writeText(text);

                        // Визуальный отклик
                        const oldIcon = ic.textContent;
                        ic.textContent = 'done'; // Иконка галочки в Material Symbols
                        btn.classList.add('copied');

                        // Если иконки не загрузились, подменим на эмодзи
                        if (ic.offsetWidth === 0) {
                            ic.textContent = '✅';
                        }

                        setTimeout(() => {
                            ic.textContent = oldIcon;
                            btn.classList.remove('copied');
                        }, 2000);
                    } catch (err) {
                        console.error('Ошибка при копировании:', err);
                    }
                });
                pre.appendChild(btn);
            });
        };
        injectButtons();
        editor.on('update', injectButtons);
        return editor;
    }

    function setLink(editor) {
        const url = prompt('Введите URL');
        if (!url) return;
        editor.chain().focus().extendMarkRange('link').setLink({ href: url, target: '_blank', rel: 'noopener' }).run();
    }

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

    const theoryEditor = createRichEditor({
        toolbarEl: 'theoryToolbar',
        editorEl: 'theoryEditor',
    });


    window.tiptapEditors = {
        theory: theoryEditor,
        tasks: [],
        tests: [],
    };
    window.tiptapHelpers = {
        createRichEditor,
        registerTestEditor(editor) {
            if (!window.tiptapEditors) {
                window.tiptapEditors = { theory: null, tasks: null, tests: [] };
            }
            window.tiptapEditors.tests = window.tiptapEditors.tests || [];
            window.tiptapEditors.tests.push(editor);
        },
        unregisterTestEditor(editor) {
            if (!window.tiptapEditors) return;
            window.tiptapEditors.tests = (window.tiptapEditors.tests || []).filter((e) => e !== editor);
        },
        registerTasksEditor(editor) {
            if (!window.tiptapEditors) {
                window.tiptapEditors = { theory: null, tasks: [], tests: [] };
            }
            window.tiptapEditors.tasks = window.tiptapEditors.tasks || [];
            window.tiptapEditors.tasks.push(editor);
        },
        unregisterTasksEditor(editor) {
            if (!window.tiptapEditors) return;
            window.tiptapEditors.tasks = (window.tiptapEditors.tasks || []).filter((e) => e !== editor);
        },
    };

    window.dispatchEvent(new CustomEvent('tiptap-ready'));
})().catch((e) => {
    console.error(e);
});
