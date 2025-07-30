// =========================
// main.js – UI/UX funkcionalumas visam projektui (Prinona)
// =========================

document.addEventListener('DOMContentLoaded', function () {
    // --- Kiti tavo UI elementai (jei jų yra) ---
    // Pvz., meniu toggle, modalai ir t.t.

    // --- Swiper produktų carousel ---
    try {
        // Naudojame tą patį selektorių kaip HTML'e: .swiper arba .mySwiper
        var swiperContainer = document.querySelector('.mySwiper');
        if (swiperContainer) {
            new Swiper('.mySwiper', {
                slidesPerView: 4,
                spaceBetween: 32,
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
                breakpoints: {
                    1280: { slidesPerView: 4 },
                    1024: { slidesPerView: 3 },
                    768: { slidesPerView: 2 },
                    0: { slidesPerView: 1 }
                }
            });
        }
    } catch (err) {
        console.error("Klaida inicijuojant Swiper carousel:", err);
    }

    // --- Pavyzdys: kitų funkcijų vieta ---
    // try {
    //     ...kitas JS kodas
    // } catch (err) {
    //     console.error("Klaida funkcijoje XYZ:", err);
    // }
});