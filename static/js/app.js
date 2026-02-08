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
