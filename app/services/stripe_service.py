import stripe
from flask import current_app
from app.utils.extensions import db
from app.models.user import User
from app.models.payment_attempt import PaymentAttempt
import logging

def create_stripe_payment_intent(user_id, amount):
    """
    Inicijuoja Stripe PaymentIntent (balanso papildymui).
    Grąžina (client_secret, klaida) – JS naudos Stripe modalui.
    """
    try:
        if not user_id or amount is None or float(amount) <= 0:
            return None, "Neteisinga suma."
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        user = db.session.get(User, user_id)
        if not user:
            return None, "Naudotojas nerastas."

        # Stripe naudoja centus (pvz. 10 EUR -> 1000)
        intent = stripe.PaymentIntent.create(
            amount=int(float(amount) * 100),
            currency="eur",
            metadata={"user_id": str(user.id)},
        )

        # Registruojam DB bandymą
        try:
            db.session.add(PaymentAttempt(
                user_id=user.id,
                session_id=intent.id,
                amount=amount,
                status="pending"
            ))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.warning(f"Nepavyko išsaugoti PaymentAttempt: {e}")

        return intent.client_secret, None
    except Exception as e:
        db.session.rollback()
        logging.error(f"Stripe PaymentIntent klaida: {e}")
        return None, str(e)

def handle_stripe_payment_success(user_id, payment_intent_id):
    """
    Patikrina ar PaymentIntent sėkmingas, papildo balansą, atnaujina PaymentAttempt.
    Grąžina (success: bool, message: str).
    """
    try:
        if not payment_intent_id:
            return False, "Trūksta Stripe PaymentIntent ID."
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if intent.status != 'succeeded':
            return False, "Mokėjimas Stripe'e dar nepatvirtintas."

        amount = intent.amount / 100  # Stripe -> EUR
        currency = intent.currency
        user = db.session.get(User, user_id)
        if not user:
            return False, "Naudotojas nerastas."

        # Anti-double-spend: tik jei dar neapdorotas
        payment_attempt = PaymentAttempt.query.filter_by(
            session_id=payment_intent_id,
            user_id=user_id
        ).first()

        if payment_attempt and payment_attempt.status == 'success':
            return False, "Šis papildymas jau apdorotas."

        # Papildom balansą
        user.balance = float(user.balance or 0) + amount

        # Atnaujinam PaymentAttempt
        if not payment_attempt:
            payment_attempt = PaymentAttempt(
                user_id=user_id,
                session_id=payment_intent_id,
                amount=amount,
                status="success"
            )
            db.session.add(payment_attempt)
        else:
            payment_attempt.status = "success"
            payment_attempt.amount = amount
            payment_attempt.error_message = None

        db.session.commit()
        return True, f"Balansas papildytas {amount:.2f} {currency.upper()}."
    except Exception as e:
        db.session.rollback()
        logging.error(f"Stripe success DB klaida: {e}")
        return False, f"Klaida papildant balansą: {str(e)}"

def handle_stripe_payment_cancel(user_id, payment_intent_id=None):
    """
    Pažymi DB, kad vartotojas atšaukė/nutraukė mokėjimą (jei reikia UI).
    """
    try:
        payment_attempt = None
        if payment_intent_id:
            payment_attempt = PaymentAttempt.query.filter_by(
                session_id=payment_intent_id,
                user_id=user_id
            ).first()
        if payment_attempt:
            payment_attempt.status = "canceled"
            db.session.commit()
        else:
            db.session.add(PaymentAttempt(
                user_id=user_id,
                session_id=payment_intent_id,
                status="canceled"
            ))
            db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logging.error(f"Klaida žymint Stripe cancel: {e}")
        return False

# (Optional) Grąžina paskutinį bandymą (naudinga UX)
def get_last_payment_attempt(user_id):
    return PaymentAttempt.query.filter_by(user_id=user_id).order_by(PaymentAttempt.created_at.desc()).first()