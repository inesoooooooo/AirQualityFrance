// Changement de carte nationale
const carteSelect = document.getElementById('carte-select');
const carteFrame = document.getElementById('carte-frame');

if (carteSelect && carteFrame) {
    carteSelect.addEventListener('change', function () {
        carteFrame.src = this.value;
    });
}

// Changement de carte ville
const villeSelect = document.getElementById('ville-select');
const villeFrame = document.getElementById('ville-frame');

if (villeSelect && villeFrame) {
    villeSelect.addEventListener('change', function () {
        villeFrame.src = this.value;
    });
}

// Animation d’apparition au scroll
const animatedSections = document.querySelectorAll('.fade-in');

const observer = new IntersectionObserver(
    entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    },
    {
        threshold: 0.15
    }
);

animatedSections.forEach(sec => observer.observe(sec));



