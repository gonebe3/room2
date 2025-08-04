from flask import Blueprint, request, jsonify, flash
from flask_login import login_required, current_user
from app.services.stripe_service import (
    create_stripe_payment_intent,
    handle_stripe_payment_success,
    handle_stripe_payment_cancel,
)

stripe_bp = Blueprint('stripe', __name__, url_prefix='/stripe')

# POST /stripe/create-payment-intent  – JS iškviečia norėdamas pradėti Stripe mokėjimą
@stripe_bp.route('/create-payment-intent', methods=['POST'])
@login_required
def create_payment_intent_route():
    data = request.get_json()
    amount = data.get("amount")
    if not amount or float(amount) < 0.5:
        return jsonify({"error": "Neteisinga suma."}), 400

    client_secret, error = create_stripe_payment_intent(current_user.id, float(amount))
    if client_secret:
        return jsonify({"client_secret": client_secret})
    else:
        return jsonify({"error": error or "Stripe klaida."}), 400

# POST /stripe/success – kviečia JS po sėkmingo mokėjimo
@stripe_bp.route('/success', methods=['POST'])
@login_required
def stripe_payment_success():
    data = request.get_json()
    payment_intent_id = data.get("payment_intent_id")
    if not payment_intent_id:
        return jsonify({"error": "Trūksta PaymentIntent ID."}), 400
    success, message = handle_stripe_payment_success(current_user.id, payment_intent_id)
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "message": message}), 400

# POST /stripe/cancel – JS kviečia jei naudotojas uždaro modalą/atšaukia
@stripe_bp.route('/cancel', methods=['POST'])
@login_required
def stripe_payment_cancel():
    data = request.get_json() or {}
    payment_intent_id = data.get("payment_intent_id")
    handle_stripe_payment_cancel(current_user.id, payment_intent_id)
    return jsonify({"success": True})