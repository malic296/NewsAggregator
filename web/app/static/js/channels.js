function syncToggle(checkbox, uuid) {
    const btn = document.getElementById('btn-' + uuid);
    const icon = btn.querySelector('i');
    const text = btn.querySelector('.btn-text');

    if (checkbox.checked) {
        btn.classList.add('is-dark', 'is-outlined');
        btn.classList.remove('is-primary');
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
        text.innerText = 'Vypnuto';
    } else {
        btn.classList.remove('is-dark', 'is-outlined');
        btn.classList.add('is-primary');
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
        text.innerText = 'Aktivní';
    }
}

document.addEventListener('error', (event) => {
    if (event.target.classList.contains('channel-logo')) {
        const img = event.target;
        const figure = img.closest('figure');

        if (figure) {
            img.style.display = 'none';

            const iconSpan = figure.querySelector('.icon');
            if (iconSpan) {
                iconSpan.style.display = 'flex';
            }
        }
    }
}, true);