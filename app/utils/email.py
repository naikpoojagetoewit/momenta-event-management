from flask import current_app
from flask_mail import Message
from app.extensions import mail


def send_email(to, subject, body_html):
    try:
        msg = Message(subject=subject, recipients=[to], html=body_html)
        mail.send(msg)
    except Exception as exc:  # noqa: BLE001
        # In dev / when SMTP isn't configured, just log to console instead of failing the request.
        current_app.logger.info(f"[EMAIL to {to}] {subject}\n{body_html}\n(send skipped: {exc})")


def send_registration_email(user):
    send_email(
        user.email,
        "Welcome to Momenta!",
        f"<h2>Hi {user.name},</h2><p>Thanks for registering with Momenta - "
        f"Creating Moments That Matter. You can now log in and start planning your event.</p>",
    )


def send_booking_confirmation_email(user, booking):
    send_email(
        user.email,
        "Booking Received - Momenta",
        f"<h2>Hi {user.name},</h2><p>Your booking #{booking.booking_id} for "
        f"{booking.event_type.event_name} on {booking.event_date} has been received and is "
        f"currently <b>{booking.status}</b>. We'll notify you once it's approved.</p>",
    )


def send_payment_success_email(user, booking, payment):
    send_email(
        user.email,
        "Payment Successful - Momenta",
        f"<h2>Hi {user.name},</h2><p>We received your payment of Rs. {payment.amount} "
        f"for booking #{booking.booking_id}. Transaction ID: {payment.transaction_id}.</p>",
    )


def send_status_update_email(user, booking):
    send_email(
        user.email,
        f"Event Update - Booking #{booking.booking_id}",
        f"<h2>Hi {user.name},</h2><p>Your event status has been updated to "
        f"<b>{booking.status}</b> (stage: {booking.manager_stage}).</p>",
    )
