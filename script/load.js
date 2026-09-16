document.addEventListener('DOMContentLoaded', () => {
    const testDiv = document.getElementById('test-div');
    const btn = document.getElementById('test-btn');
    
    const hasVisited = sessionStorage.getItem('hasVisitedBefore');

    if (!hasVisited) {
        testDiv.classList.remove('hidden');
        sessionStorage.setItem('hasVisitedBefore', 'true');
    }

    btn.addEventListener('click', () => {
        testDiv.classList.add('hidden');
    });
});