from flask_mail import Message
from flask import current_app, render_template
from app.utils.extensions import mail
from threading import Thread

def send_async_email(app, msg):
    """Pagalbinė funkcija, kad siųsti email'us asinchroniškai (neblokuoja užklausos)."""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            # Čia galite loginti klaidas į failą ar monitoringą
            print(f"Email siuntimo klaida: {e}")

def send_email(subject, recipients, template_name, context=None, html=True, attachments=None, cc=None, bcc=None, sender=None):
    """
    Siunčia el. laišką su HTML arba paprastu tekstu, naudojant Flask-Mail ir Jinja2 šablonus.

    :param subject: Laiško tema (string)
    :param recipients: Sąrašas gavėjų el. paštų
    :param template_name: Šablono failo pavadinimas be 'email/' prefikso (pvz., 'confirmation.html')
    :param context: dict su šablono kintamaisiais
    :param html: Ar siųsti HTML (True) ar paprastą tekstą (False)
    :param attachments: Sąrašas tuple: (failo_pavadinimas, mime_tip, data_bytes)
    :param cc: Sąrašas CC gavėjų
    :param bcc: Sąrašas BCC gavėjų
    :param sender: Kas nurodomas kaip siuntėjas (default – config)
    :return: None
    """
    app = current_app._get_current_object()
    context = context or {}

    msg = Message(
        subject=subject,
        sender=sender or app.config.get('MAIL_DEFAULT_SENDER'),
        recipients=recipients,
        cc=cc or [],
        bcc=bcc or [],
    )

    if html:
        msg.html = render_template(f"email/{template_name}", **context)
    else:
        msg.body = render_template(f"email/{template_name}", **context)

    if attachments:
        for fname, mime, data in attachments:
            msg.attach(fname, mime, data)

    # Siunčiame per atskirą Thread (nekliudo request-ui)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

# --- Naudojimo pavyzdžiai (galima ištrinti jei nereikės) ---

def send_confirmation_email(user, token):
    """
    Siunčia registracijos patvirtinimo laišką vartotojui.
    :param user: User objektas
    :param token: Patvirtinimo tokenas
    """
    confirmation_url = f"{current_app.config['BASE_URL']}/auth/confirm/{token}"
    logo_url = f"{current_app.config.get('LOGO_URL', '')}"
    context = {
        "user": user,
        "confirmation_url": confirmation_url,
        "logo_url": logo_url,
    }
    subject = "Patvirtinkite savo el. pašto adresą"
    send_email(
        subject=subject,
        recipients=[user.email],
        template_name="confirmation.html",
        context=context,
        html=True
    )

def send_promo_email(user, promo):
    """
    Siunčia promo laišką.
    :param user: User objektas
    :param promo: dict su promo duomenimis (promo_title, promo_text, promo_code, ir pan.)
    """
    context = {**promo, "logo_url": current_app.config.get('LOGO_URL', '')}
    subject = promo.get("promo_title", "Specialus pasiūlymas iš Prinona!")
    send_email(
        subject=subject,
        recipients=[user.email],
        template_name="promo.html",
        context=context,
        html=True
    )