document.addEventListener('DOMContentLoaded', () => {
    const testDiv = document.getElementById('wlc-div');
    const btn = document.getElementById('wlc-btn');
    
    const hasVisited = sessionStorage.getItem('hasVisitedBefore');

    if (!hasVisited) {
        testDiv.classList.remove('wlc-hidden');
        sessionStorage.setItem('hasVisitedBefore', 'true');
    }

    btn.addEventListener('click', () => {
        testDiv.classList.add('wlc-hidden');
    });
});