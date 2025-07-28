// =========================
// Prinona main.js – UI/UX funkcionalumas visam projektui
// =========================

document.addEventListener('DOMContentLoaded', function () {

    // --- 1. Mobilios navigacijos valdymas (hamburger / close perjungimas) ---
    const menuToggle = document.querySelector('.menu-toggle');
    const menuClose = document.querySelector('.menu-close');
    const navbar = document.querySelector('.main-navbar');

    if (menuToggle && menuClose && navbar) {
        // Atidaro meniu, paslepia hamburger, rodo close
        menuToggle.addEventListener('click', function () {
            navbar.classList.add('menu-open');
            menuToggle.style.display = 'none';
            menuClose.style.display = 'inline-flex';
        });
        // Uždaro meniu, rodo hamburger, paslepia close
        menuClose.addEventListener('click', function () {
            navbar.classList.remove('menu-open');
            menuToggle.style.display = 'inline-flex';
            menuClose.style.display = 'none';
        });
    }

    // --- 2. Flash žinučių automatinis uždarymas po 3,5 s ---
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.style.display = 'none';
            }, 500);
        }, 3500);
    });

    // --- 3. "Scroll to Top" mygtukas (pridėti į layout, jei reikės) ---
    const scrollBtn = document.getElementById('scrollToTopBtn');
    if (scrollBtn) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 300) {
                scrollBtn.style.display = 'flex';
            } else {
                scrollBtn.style.display = 'none';
            }
        });
        scrollBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // --- 4. (Rezervuota) Inputų validacija, AJAX funkcijos, papildomi UX patobulinimai ---
    // Pvz., galima integruoti realaus laiko input validacijas arba AJAX operacijas.
    // Funkcionalumas bus papildytas, kai bus kuriami atskiri puslapiai/formos.

});