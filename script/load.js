document.addEventListener('DOMContentLoaded', () => {
    const testDiv = document.getElementById('wlc-div');
    const btn = document.getElementById('wlc-btn');

    testDiv.classList.remove('wlc-hidden');

    btn.addEventListener('click', () => {
        testDiv.classList.add('wlc-hidden');
    });
});