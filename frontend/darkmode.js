document.addEventListener('DOMContentLoaded', () => {
    const themingSwitcher = document.getElementById('themingSwitcher');

    const savedTheme = localStorage.getItem('theme') || 'light';

    if (savedTheme === 'dark') {
        document.body.classList.add('custom-dark');
        if (themingSwitcher) themingSwitcher.checked = true;
    }

    if (themingSwitcher) {
        themingSwitcher.addEventListener('change', () => {
            if (themingSwitcher.checked) {
                document.body.classList.add('custom-dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('custom-dark');
                localStorage.setItem('theme', 'light');
            }
        });
    }
});