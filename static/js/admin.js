// Назначение файла: логика редактора урока (тесты, подготовка данных для формы).

const lessonForm = document.getElementById('lessonForm');
const testsListEl = document.getElementById('testsList');
const addTestBtn = document.getElementById('addTest');
const theoryHtmlEl = document.getElementById('theoryHtml');
const testsJsonEl = document.getElementById('testsJson');
const tasksJsonEl = document.getElementById('tasksJson');

const initialLessonData = window.initialLessonData || { theory_html: '', tasks: [], tests: [] };
const testEditors = new Map();
let testCounter = 0;
let tiptapReady = false;
const pendingTestQueue = [];

// Добавление тестового вопроса.
function addTestItem(data = null) {
    if (!testsListEl) return;
    if (!tiptapReady) {
        pendingTestQueue.push(data);
        return;
    }

    const testId = `test-${testCounter++}`;
    const wrapper = document.createElement('div');
    wrapper.className = 'test-editor';
    wrapper.dataset.testId = testId;

    const questionBlock = document.createElement('div');
    questionBlock.className = 'test-question-block';

    const questionLabel = document.createElement('div');
    questionLabel.className = 'test-question-label';
    questionLabel.textContent = 'Вопрос';

    const questionToolbar = document.createElement('div');
    questionToolbar.className = 'editor-toolbar test-toolbar';

    const questionEditor = document.createElement('div');
    questionEditor.className = 'editor test-question-editor';
    questionEditor.dataset.testId = testId;

    questionBlock.append(questionLabel, questionToolbar, questionEditor);
    wrapper.appendChild(questionBlock);

    let editorInstance = null;
    if (window.tiptapHelpers?.createRichEditor) {
        editorInstance = window.tiptapHelpers.createRichEditor({
            toolbarEl: questionToolbar,
            editorEl: questionEditor,
        });
        if (editorInstance) {
            window.tiptapHelpers.registerTestEditor(editorInstance);
            editorInstance.commands.setContent(data?.question || '');
        }
    }
    if (!editorInstance) {
        questionEditor.textContent = data?.question || '';
    }
    testEditors.set(testId, editorInstance);

    const optionsGrid = document.createElement('div');
    optionsGrid.className = 'options-grid';

    const correctIndex = data?.correct_index ?? 0;

    for (let i = 0; i < 4; i++) {
        const row = document.createElement('div');
        row.className = 'option-row';

        const input = document.createElement('input');
        input.type = 'text';
        input.placeholder = `Вариант ${i + 1}`;
        input.className = 'option-input';
        input.value = data?.options?.[i] || '';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = i === correctIndex;
        checkbox.title = 'Правильный ответ';
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                optionsGrid.querySelectorAll('input[type="checkbox"]').forEach((c, idx) => {
                    if (idx !== i) c.checked = false;
                });
            }
        });

        row.appendChild(input);
        row.appendChild(checkbox);
        optionsGrid.appendChild(row);
    }

    const removeBtn = document.createElement('button');
    removeBtn.className = 'btn danger';
    removeBtn.type = 'button';
    removeBtn.textContent = 'Удалить вопрос';
    removeBtn.addEventListener('click', () => {
        wrapper.remove();
        testEditors.delete(testId);
        if (editorInstance) {
            window.tiptapHelpers?.unregisterTestEditor?.(editorInstance);
        }
    });

    wrapper.appendChild(optionsGrid);
    wrapper.appendChild(removeBtn);
    testsListEl.appendChild(wrapper);
}

addTestBtn?.addEventListener('click', () => addTestItem());

// Сбор тестов.
function collectTests() {
    if (!testsListEl) return [];

    const items = [];
    testsListEl.querySelectorAll('.test-editor').forEach((editorWrapper) => {
        const testId = editorWrapper.dataset.testId;
        const richEditor = testEditors.get(testId);
        const questionNode = editorWrapper.querySelector('.test-question-editor');
        let question = '';
        if (richEditor?.getHTML) {
            question = richEditor.getHTML();
        } else {
            question = questionNode?.textContent?.trim() || '';
        }
        const optionInputs = editorWrapper.querySelectorAll('.options-grid input[type="text"]');
        const options = Array.from(optionInputs).map((input) => input.value.trim());
        const checkboxes = editorWrapper.querySelectorAll('.options-grid input[type="checkbox"]');
        const correctIndex = Array.from(checkboxes).findIndex((c) => c.checked);
        items.push({
            question,
            options,
            correct_index: correctIndex < 0 ? 0 : correctIndex,
        });
    });
    return items;
}

// Извлечение задач из editor (разделяем по заголовкам h3).
function extractTasksFromEditor() {
    const html = window.tiptapEditors?.tasks?.getHTML() || '';
    const container = document.createElement('div');
    container.innerHTML = html;
    const tasks = [];
    let current = null;

    Array.from(container.childNodes).forEach((node) => {
        if (node.tagName === 'H3') {
            if (current) tasks.push(current);
            current = { title: node.textContent || 'Задача', html: '' };
        } else {
            if (!current) current = { title: 'Задача', html: '' };
            current.html += node.outerHTML || node.textContent;
        }
    });

    if (current) tasks.push(current);
    return tasks;
}

function hydrateEditors() {
    if (window.tiptapEditors?.theory) {
        window.tiptapEditors.theory.commands.setContent(initialLessonData.theory_html || '');
    }

    if (window.tiptapEditors?.tasks) {
        const tasksHtml = (initialLessonData.tasks || [])
            .map((task) => `<h3>${task.title}</h3>${task.html}`)
            .join('');
        window.tiptapEditors.tasks.commands.setContent(tasksHtml);
    }

    if (testsListEl) {
        testEditors.forEach((editor) => {
            if (editor) {
                window.tiptapHelpers?.unregisterTestEditor?.(editor);
            }
        });
        testEditors.clear();
        testsListEl.innerHTML = '';
        (initialLessonData.tests || []).forEach((t) => addTestItem(t));
    }
}

lessonForm?.addEventListener('submit', () => {
    if (theoryHtmlEl) {
        theoryHtmlEl.value = window.tiptapEditors?.theory?.getHTML() || '';
    }
    if (testsJsonEl) {
        testsJsonEl.value = JSON.stringify(collectTests());
    }
    if (tasksJsonEl) {
        tasksJsonEl.value = JSON.stringify(extractTasksFromEditor());
    }
});

window.addEventListener('tiptap-ready', () => {
    tiptapReady = true;
    hydrateEditors();
    while (pendingTestQueue.length) {
        addTestItem(pendingTestQueue.shift());
    }
});
