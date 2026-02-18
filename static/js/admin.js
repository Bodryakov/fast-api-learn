// Назначение файла: логика редактора урока (тесты, задачи, подготовка данных для формы).

const lessonForm = document.getElementById('lessonForm');
const testsListEl = document.getElementById('testsList');
const addTestBtn = document.getElementById('addTest');
const tasksListEl = document.getElementById('tasksList');
const addTaskBtn = document.getElementById('addTask');
const theoryHtmlEl = document.getElementById('theoryHtml');
const testsJsonEl = document.getElementById('testsJson');
const tasksJsonEl = document.getElementById('tasksJson');

const initialLessonData = window.initialLessonData || { theory_html: '', tasks: [], tests: [] };
const testEditors = new Map();
const taskEditors = new Map();
let testCounter = 0;
let taskCounter = 0;
let tiptapReady = false;
const pendingTestQueue = [];
const pendingTaskQueue = [];

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

// Добавление задачи.
function addTaskItem(data = null) {
    if (!tasksListEl) return;
    if (!tiptapReady) {
        pendingTaskQueue.push(data);
        return;
    }

    const taskId = `task-${taskCounter++}`;
    const wrapper = document.createElement('div');
    wrapper.className = 'task-editor lesson-panel'; // reusing lesson-panel style for padding/border if appropriate, or just a new class
    wrapper.style.border = '1px solid #ddd';
    wrapper.style.padding = '1rem';
    wrapper.style.marginBottom = '1rem';
    wrapper.style.borderRadius = 'var(--radius)';
    wrapper.dataset.taskId = taskId;

    // Title input
    const titleInput = document.createElement('input');
    titleInput.type = 'text';
    titleInput.className = 'task-title-input'; // Add specific class for selection
    titleInput.value = data?.title || '';
    titleInput.placeholder = 'Введите заголовок задачи';
    titleInput.style.width = '100%';
    titleInput.style.marginBottom = '1rem';

    wrapper.appendChild(titleInput);

    // Editor
    const editorToolbar = document.createElement('div');
    editorToolbar.className = 'editor-toolbar';
    editorToolbar.id = `task-toolbar-${taskId}`;

    const editorContent = document.createElement('div');
    editorContent.className = 'editor';
    editorContent.id = `task-editor-${taskId}`;

    wrapper.appendChild(editorToolbar);
    wrapper.appendChild(editorContent);

    let editorInstance = null;
    if (window.tiptapHelpers?.createRichEditor) {
        editorInstance = window.tiptapHelpers.createRichEditor({
            toolbarEl: editorToolbar,
            editorEl: editorContent,
        });
        if (editorInstance) {
            window.tiptapHelpers.registerTasksEditor(editorInstance);
            editorInstance.commands.setContent(data?.html || '');
        }
    }
    taskEditors.set(taskId, editorInstance);

    // Remove button
    const removeBtn = document.createElement('button');
    removeBtn.className = 'btn danger';
    removeBtn.type = 'button';
    removeBtn.textContent = 'Удалить задачу';
    removeBtn.style.marginTop = '1rem';
    removeBtn.addEventListener('click', () => {
        wrapper.remove();
        taskEditors.delete(taskId);
        if (editorInstance) {
            window.tiptapHelpers?.unregisterTasksEditor?.(editorInstance);
        }
    });

    wrapper.appendChild(removeBtn);
    tasksListEl.appendChild(wrapper);
}

addTestBtn?.addEventListener('click', () => addTestItem());
addTaskBtn?.addEventListener('click', () => addTaskItem());

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

// Сбор задач.
function collectTasks() {
    if (!tasksListEl) return [];

    const items = [];
    tasksListEl.querySelectorAll('.task-editor').forEach((editorWrapper) => {
        const taskId = editorWrapper.dataset.taskId;
        const richEditor = taskEditors.get(taskId);
        const titleInput = editorWrapper.querySelector('.task-title-input');

        let html = '';
        if (richEditor?.getHTML) {
            html = richEditor.getHTML();
        }

        items.push({
            title: titleInput?.value?.trim() || 'Задача',
            html: html,
        });
    });
    return items;
}

function hydrateEditors() {
    if (window.tiptapEditors?.theory) {
        window.tiptapEditors.theory.commands.setContent(initialLessonData.theory_html || '');
    }

    // Hydrate Tests
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

    // Hydrate Tasks
    if (tasksListEl) {
        taskEditors.forEach((editor) => {
            if (editor) {
                window.tiptapHelpers?.unregisterTasksEditor?.(editor);
            }
        });
        taskEditors.clear();
        tasksListEl.innerHTML = '';
        (initialLessonData.tasks || []).forEach((t) => addTaskItem(t));
    }
}

lessonForm?.addEventListener('submit', () => {
    if (theoryHtmlEl) {
        let html = window.tiptapEditors?.theory?.getHTML() || '';
        // Replace ProseMirror-trailingBreak and empty paragraphs with &nbsp;
        html = html.replace(/<p><br class="ProseMirror-trailingBreak"><\/p>/g, '<p>&nbsp;</p>');
        html = html.replace(/<p><\/p>/g, '<p>&nbsp;</p>');
        html = html.replace(/<p> <\/p>/g, '<p>&nbsp;</p>');
        theoryHtmlEl.value = html;
    }
    if (testsJsonEl) {
        testsJsonEl.value = JSON.stringify(collectTests());
    }
    if (tasksJsonEl) {
        tasksJsonEl.value = JSON.stringify(collectTasks());
    }
});

window.addEventListener('tiptap-ready', () => {
    tiptapReady = true;
    hydrateEditors();
    while (pendingTestQueue.length) {
        addTestItem(pendingTestQueue.shift());
    }
    while (pendingTaskQueue.length) {
        addTaskItem(pendingTaskQueue.shift());
    }
});
