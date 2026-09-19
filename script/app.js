const sickle = document.getElementById('sickle');
let x = 0, y = 0, ticking = false;

addEventListener('pointermove', e => {
    x = e.clientX;
    y = e.clientY;
    sickle.classList.add('on');
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
        sickle.style.translate = `${x}px ${y}px`;
        ticking = false;
    });
}, { passive: true });

document.documentElement.addEventListener('mouseleave', () => {
    sickle.classList.remove('on');
});













const GOAL      = 1;      // cuts needed to get a quote
const STALKS    = 50;     // how many wheat stalks to plant
const SWING_MS  = 650;    // total length of one sickle swing
const HIT_MS    = 250;    // when the blade "hits" during the swing


async function getQuote() {
    try {
        return 'Your quote will appear here!';
    } catch (err) {
        return "Couldn't harvest a quote this time. Try cutting another one!";
    }
}







const harvest   = document.getElementById('harvest');
    const field     = document.getElementById('field');
    const card      = document.getElementById('quote-card');
    const quoteText = document.getElementById('quote-text');
    const quoteBtn  = document.getElementById('quote-close');

    let count = 0;
    let swinging = false;


    function plant() {
        field.innerHTML = '';
        for (let i = 0; i < STALKS; i++) {
            const s = document.createElement('div');
            const depth = Math.random();                       // 0 = far, 1 = near
            s.className = 'stalk';
            s.style.backgroundImage = `url("images/wheat-${1 + Math.floor(Math.random() * 3)}.png")`;
            s.style.left = Math.random() * 96 + '%';
            s.style.bottom = (1 - depth) * 18 + 'vh';          // near stalks sit lower...
            s.style.scale = 0.6 + depth * 0.7;                 // ...and bigger
            s.style.zIndex = Math.round(depth * 100);
            s.style.animationDelay = (-Math.random() * 3) + 's';
            field.appendChild(s);
        }
    }

    function swing(stalk) {
        swinging = true;

        sickle.animate([
            { rotate: '0deg',   easing: 'ease-out' },                 // rest
            { rotate: '40deg',  offset: 0.3,  easing: 'ease-in' },    // pull back
            { rotate: '-35deg', offset: 0.55, easing: 'ease-out' },   // slash
            { rotate: '0deg' }                                        // return
        ], { duration: SWING_MS }).onfinish = () => { swinging = false; };

        if (stalk) setTimeout(() => cut(stalk), HIT_MS);              // the moment of impact
    }

    function cut(stalk) {
        // the top half: a clipped copy that falls off
        const top = stalk.cloneNode();
        top.classList.add('top-piece');
        top.style.animationDelay = '0s';
        top.addEventListener('animationend', () => top.remove());
        field.appendChild(top);

        // the bottom half: turns into stubble
        stalk.classList.add('cut');
        stalk.style.backgroundImage = 'url("images/stubble.png")';

        count++;
        if (count === GOAL) setTimeout(showQuote, 700);
    }

    async function showQuote() {
        quoteText.textContent = 'Harvesting your quote...';
        card.hidden = false;
        quoteText.textContent = await getQuote();
    }

    // click anywhere in the field section: swing, and cut if a stalk was hit
    harvest.addEventListener('click', e => {
        if (swinging || count >= GOAL) return;
        swing(e.target.closest('.stalk:not(.cut)'));
    });

    quoteBtn.addEventListener('click', () => {
        card.hidden = true;
        count = 0;
        plant();                                                      // the wheat regrows
    });

    plant();
    updateHud();