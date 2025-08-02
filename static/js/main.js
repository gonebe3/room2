// =========================
// main.js – UI/UX funkcionalumas visam projektui (Prinona)
// =========================

document.addEventListener('DOMContentLoaded', function () {
    // --- Swiper produktų carousel ---
    try {
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
});

// ----------- STRIPE BALANCE (PaymentIntent) JS -------------
document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("stripe-balance-form");
    if (!form) return;

    // Stripe
    const stripe = Stripe(window.STRIPE_KEY);
    const elements = stripe.elements();
    const card = elements.create('card', {
        style: {
            base: {
                fontSize: '16px',
                color: '#232946',
                fontFamily: 'Montserrat, Arial, sans-serif',
                '::placeholder': { color: '#888' },
            }
        
        }
    });
    card.mount("#card-element");

    const errorBox = document.getElementById("stripe-error");
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    form.addEventListener("submit", async function(e) {
        e.preventDefault();
        errorBox.style.display = "none";
        const amount = parseFloat(document.getElementById("balance-amount").value.replace(",", "."));
        if (isNaN(amount) || amount < 0.5) {
            errorBox.textContent = "Suma turi būti ne mažesnė nei 0.50 €.";
            errorBox.style.display = "block";
            return;
        }

        // Sukuriam PaymentIntent per AJAX POST
        let clientSecret;
        try {
            const res = await fetch("/stripe/create-payment-intent", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ amount: amount })
            });
            const data = await res.json();
            if (!data.client_secret) {
                errorBox.textContent = data.error || "Nepavyko inicijuoti Stripe mokėjimo.";
                errorBox.style.display = "block";
                return;
            }
            clientSecret = data.client_secret;
        } catch (err) {
            errorBox.textContent = "Klaida jungiantis prie Stripe: " + (err.message || err);
            errorBox.style.display = "block";
            return;
        }

        // Parodome Stripe Elements kortelės modalą
        const {error, paymentIntent} = await stripe.confirmCardPayment(clientSecret, {
            payment_method: { card: card }
        });

        if (error) {
            errorBox.textContent = error.message || "Mokėjimas nepavyko.";
            errorBox.style.display = "block";
            return;
        }

        if (paymentIntent && paymentIntent.status === "succeeded") {
            // Po sėkmingo mokėjimo – POST į /stripe/success, kad papildytų balansą DB
            fetch("/stripe/success", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ payment_intent_id: paymentIntent.id })
            })
            .then(resp => resp.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    errorBox.textContent = data.message || "Nepavyko papildyti balanso.";
                    errorBox.style.display = "block";
                }
            });
        }
    });
});
