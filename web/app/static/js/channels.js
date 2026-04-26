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