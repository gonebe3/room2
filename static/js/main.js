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
    if (!form) {
        console.log("Stripe form not found");
        return;
    }

    // Patikrinkime ar Stripe yra užkrautas
    if (typeof Stripe === 'undefined') {
        console.error("Stripe.js nepavyko užkrauti");
        return;
    }

    if (!window.STRIPE_KEY) {
        console.error("STRIPE_KEY nerastas");
        return;
    }

    // Stripe
    const stripe = Stripe(window.STRIPE_KEY);
    const elements = stripe.elements();
    
    // Patikrinkime ar elementai egzistuoja DOM'e
    const cardNumberDiv = document.getElementById("card-number-element");
    const cardExpiryDiv = document.getElementById("card-expiry-element");
    const cardCvcDiv = document.getElementById("card-cvc-element");
    
    if (!cardNumberDiv || !cardExpiryDiv || !cardCvcDiv) {
        console.error("Stripe elementų div'ai nerasti DOM'e");
        return;
    }
    
    // Sukuriame ATSKIRAIS elementus
    const cardNumber = elements.create('cardNumber', {
        style: {
            base: {
                fontSize: '16px',
                color: '#232946',
                fontFamily: 'Montserrat, Arial, sans-serif',
                '::placeholder': { color: '#888' },
            }
        }
    });
    
    const cardExpiry = elements.create('cardExpiry', {
        style: {
            base: {
                fontSize: '16px',
                color: '#232946',
                fontFamily: 'Montserrat, Arial, sans-serif',
                '::placeholder': { color: '#888' },
            }
        }
    });
    
    const cardCvc = elements.create('cardCvc', {
        style: {
            base: {
                fontSize: '16px',
                color: '#232946',
                fontFamily: 'Montserrat, Arial, sans-serif',
                '::placeholder': { color: '#888' },
            }
        }
    });

    // Mount'iname kiekvieną elementą atskirai
    try {
        cardNumber.mount("#card-number-element");
        cardExpiry.mount("#card-expiry-element");
        cardCvc.mount("#card-cvc-element");
        console.log("Stripe elementai sėkmingai užkrauti");
    } catch (error) {
        console.error("Klaida mount'inant Stripe elementus:", error);
        return;
    }

    const errorBox = document.getElementById("stripe-error");
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    
    if (!csrfToken) {
        console.error("CSRF token nerastas");
        return;
    }

    // Real-time klaidų apdorojimas
    cardNumber.on('change', function(event) {
        if (event.error) {
            errorBox.textContent = event.error.message;
            errorBox.style.display = "block";
        } else {
            errorBox.style.display = "none";
        }
    });

    form.addEventListener("submit", async function(e) {
        e.preventDefault();
        console.log("Form submitted");
        
        errorBox.style.display = "none";
        
        const amountInput = document.getElementById("balance-amount");
        if (!amountInput) {
            console.error("Amount input nerastas");
            return;
        }
        
        const amount = parseFloat(amountInput.value.replace(",", "."));
        console.log("Amount:", amount);
        
        if (isNaN(amount) || amount < 0.5) {
            errorBox.textContent = "Suma turi būti ne mažesnė nei 0.50 €.";
            errorBox.style.display = "block";
            return;
        }

        // Sukuriam PaymentIntent per AJAX POST
        let clientSecret;
        try {
            console.log("Sending request to create payment intent...");
            const res = await fetch("/stripe/create-payment-intent", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken.getAttribute('content')
                },
                body: JSON.stringify({ amount: amount })
            });
            
            const data = await res.json();
            console.log("Payment intent response:", data);
            
            if (!data.client_secret) {
                errorBox.textContent = data.error || "Nepavyko inicijuoti Stripe mokėjimo.";
                errorBox.style.display = "block";
                return;
            }
            clientSecret = data.client_secret;
        } catch (err) {
            console.error("Fetch error:", err);
            errorBox.textContent = "Klaida jungiantis prie Stripe: " + (err.message || err);
            errorBox.style.display = "block";
            return;
        }

        // Patvirtinkime mokėjimą
        console.log("Confirming payment...");
        const {error, paymentIntent} = await stripe.confirmCardPayment(clientSecret, {
            payment_method: { 
                card: cardNumber // Naudojame cardNumber elementą
            }
        });

        if (error) {
            console.error("Payment error:", error);
            errorBox.textContent = error.message || "Mokėjimas nepavyko.";
            errorBox.style.display = "block";
            return;
        }

        if (paymentIntent && paymentIntent.status === "succeeded") {
            console.log("Payment succeeded, updating balance...");
            // Po sėkmingo mokėjimo – POST į /stripe/success
            try {
                const response = await fetch("/stripe/success", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken.getAttribute('content')
                    },
                    body: JSON.stringify({ payment_intent_id: paymentIntent.id })
                });
                
                const data = await response.json();
                console.log("Success response:", data);
                
                if (data.success) {
                    window.location.reload();
                } else {
                    errorBox.textContent = data.message || "Nepavyko papildyti balanso.";
                    errorBox.style.display = "block";
                }
            } catch (err) {
                console.error("Success endpoint error:", err);
                errorBox.textContent = "Klaida apdorojant mokėjimą.";
                errorBox.style.display = "block";
            }
        }
    });
});

// JavaScript for dynamic display of discount form fields based on selected type

document.addEventListener('DOMContentLoaded', () => {
  const typeSelect = document.querySelector('select[name="discount_type"]');
  const percentFields = document.querySelectorAll('.percent-field');
  const fixedFields = document.querySelectorAll('.fixed-field');
  const loyaltyFields = document.querySelectorAll('.loyalty-field');

  function updateFields() {
    const val = typeSelect.value;
    percentFields.forEach(el => el.style.display = val === 'percent' ? 'block' : 'none');
    fixedFields.forEach(el => el.style.display = val === 'fixed' ? 'block' : 'none');
    loyaltyFields.forEach(el => el.style.display = val === 'loyalty' ? 'block' : 'none');
  }

  typeSelect.addEventListener('change', updateFields);
  updateFields();
});
