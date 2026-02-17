// Назначение файла: клиентская логика сайта (тема, тесты, общие функции).

// Переключение светлой/тёмной темы.
const themeToggle = document.getElementById('themeToggle');
const root = document.documentElement;

// Загружаем тему из localStorage.
const storedTheme = localStorage.getItem('theme');
if (storedTheme) {
    root.setAttribute('data-theme', storedTheme);
}

// Обработчик смены темы.
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const current = root.getAttribute('data-theme');
        const next = current === 'dark' ? '' : 'dark';
        if (next) {
            root.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
        } else {
            root.removeAttribute('data-theme');
            localStorage.removeItem('theme');
        }
    });
}

// Логика прохождения тестов.
const testBlocks = document.querySelectorAll('.test-question');

testBlocks.forEach((block) => {
    const correctIndex = Number(block.dataset.correct);
    const options = block.querySelectorAll('.test-option');
    let answered = false;

    options.forEach((btn) => {
        btn.addEventListener('click', () => {
            if (answered) return;
            answered = true;

            const index = Number(btn.dataset.index);

            options.forEach((optionBtn) => {
                const optIndex = Number(optionBtn.dataset.index);
                if (optIndex === correctIndex) {
                    optionBtn.classList.add('correct');
                } else if (optIndex === index) {
                    optionBtn.classList.add('wrong');
                }
            });
        });
    });
});

function addCopyButtonsToCodeBlocks(root = document) {
    const blocks = root.querySelectorAll('.lesson-theory pre, .task-text pre, pre');
    blocks.forEach((pre) => {
        if (pre.dataset.copyInit) return;
        pre.dataset.copyInit = '1';
        
        pre.style.position = 'relative';
        
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'code-copy-btn';
        btn.title = 'Скопировать';
        
        const ic = document.createElement('span');
        ic.className = 'material-symbols-rounded';
        ic.textContent = 'content_copy';
        btn.appendChild(ic);
        
        btn.addEventListener('click', async () => {
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
}

document.addEventListener('DOMContentLoaded', () => {
    addCopyButtonsToCodeBlocks(document);
});
