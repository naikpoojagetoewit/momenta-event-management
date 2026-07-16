import secrets
from datetime import datetime
from flask import (Blueprint, render_template, request, redirect, url_for,
                    flash, jsonify, send_from_directory, current_app)
from flask_login import login_required, current_user
from app.extensions import db
from app.models import EventType, Service, Booking, Payment, Feedback
from app.utils.decorators import role_required
from app.utils.budget import calculate_exact_total, predict_budget_ai
from app.utils.invoice import generate_invoice_pdf
from app.utils.email import send_booking_confirmation_email, send_payment_success_email

client_bp = Blueprint('client', __name__, template_folder='../templates/client')


@client_bp.route('/dashboard')
@login_required
@role_required('client')
def dashboard():
    bookings = (Booking.query.filter_by(user_id=current_user.user_id)
                .order_by(Booking.created_at.desc()).all())
    stats = {
        'total': len(bookings),
        'pending': sum(1 for b in bookings if b.status == 'Pending'),
        'active': sum(1 for b in bookings if b.status in ('Approved', 'Assigned', 'In Progress')),
        'completed': sum(1 for b in bookings if b.status == 'Completed'),
    }
    return render_template('client/dashboard.html', bookings=bookings[:5], stats=stats)


@client_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('client')
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('client.profile'))
    return render_template('client/profile.html')


@client_bp.route('/change-password', methods=['POST'])
@login_required
@role_required('client')
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
    elif new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
    else:
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password changed successfully.', 'success')
    return redirect(url_for('client.profile'))


@client_bp.route('/book-event', methods=['GET', 'POST'])
@login_required
@role_required('client')
def book_event():
    events = EventType.query.filter_by(is_active=True).all()
    services = Service.query.filter_by(is_active=True).all()
    grouped_services = {}
    for s in services:
        grouped_services.setdefault(s.category, []).append(s)

    if request.method == 'POST':
        event_id = request.form.get('event_id', type=int)
        service_ids = request.form.getlist('service_ids', type=int)
        guest_count = request.form.get('guest_count', type=int, default=0)

        event = EventType.query.get_or_404(event_id)
        selected_services = Service.query.filter(Service.service_id.in_(service_ids)).all()
        total = calculate_exact_total(event.base_price, selected_services, guest_count)

        booking = Booking(
            user_id=current_user.user_id,
            event_id=event_id,
            event_date=datetime.strptime(request.form.get('event_date'), '%Y-%m-%d').date(),
            event_time=request.form.get('event_time'),
            house_no=request.form.get('house_no'),
            street=request.form.get('street'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            pincode=request.form.get('pincode'),
            venue=request.form.get('venue'),
            guest_count=guest_count,
            description=request.form.get('description'),
            total_amount=total,
            status='Pending',
        )
        booking.services = selected_services
        db.session.add(booking)
        db.session.commit()

        send_booking_confirmation_email(current_user, booking)
        flash('Booking submitted! Proceed to payment to confirm your slot.', 'success')
        return redirect(url_for('client.payment', booking_id=booking.booking_id))

    return render_template('client/book_event.html', events=events, grouped_services=grouped_services)


@client_bp.route('/api/budget-estimate')
@login_required
def budget_estimate():
    """AJAX endpoint powering the live Budget Calculator + AI suggested range."""
    event_id = request.args.get('event_id', type=int)
    guest_count = request.args.get('guest_count', type=int, default=0)
    service_ids = request.args.getlist('service_ids', type=int)

    event = EventType.query.get(event_id) if event_id else None
    base_price = event.base_price if event else 0
    selected_services = Service.query.filter(Service.service_id.in_(service_ids)).all() if service_ids else []

    exact_total = calculate_exact_total(base_price, selected_services, guest_count)
    ai_range = predict_budget_ai(base_price, guest_count, num_services_expected=max(len(selected_services), 4))

    return jsonify({
        'exact_total': exact_total,
        'ai_estimate_low': ai_range['low'],
        'ai_estimate_high': ai_range['high'],
    })


@client_bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
@login_required
@role_required('client')
def payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.user_id:
        flash('Not authorized.', 'danger')
        return redirect(url_for('client.dashboard'))

    if request.method == 'POST':
        method = request.form.get('method')
        # Simulated payment gateway (swap in real Razorpay checkout using the
        # RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET from .env for production use).
        txn_id = 'MOM' + secrets.token_hex(8).upper()
        payment_record = Payment(
            booking_id=booking.booking_id,
            amount=booking.total_amount,
            method=method,
            transaction_id=txn_id,
            payment_status='Success',
        )
        booking.status = 'Approved'
        db.session.add(payment_record)
        db.session.commit()

        send_payment_success_email(current_user, booking, payment_record)
        flash('Payment successful! Your event has been booked.', 'success')
        return redirect(url_for('client.booking_detail', booking_id=booking.booking_id))

    return render_template('client/payment.html', booking=booking,
                            razorpay_key=current_app.config['RAZORPAY_KEY_ID'])


@client_bp.route('/my-bookings')
@login_required
@role_required('client')
def my_bookings():
    bookings = (Booking.query.filter_by(user_id=current_user.user_id)
                .order_by(Booking.created_at.desc()).all())
    return render_template('client/my_bookings.html', bookings=bookings)


@client_bp.route('/booking/<int:booking_id>')
@login_required
@role_required('client')
def booking_detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.user_id:
        flash('Not authorized.', 'danger')
        return redirect(url_for('client.dashboard'))
    return render_template('client/booking_detail.html', booking=booking)


@client_bp.route('/booking/<int:booking_id>/invoice')
@login_required
@role_required('client')
def download_invoice(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.user_id:
        flash('Not authorized.', 'danger')
        return redirect(url_for('client.dashboard'))
    filepath, filename = generate_invoice_pdf(booking)
    return send_from_directory(current_app.config['INVOICE_FOLDER'], filename, as_attachment=True)


@client_bp.route('/booking/<int:booking_id>/feedback', methods=['GET', 'POST'])
@login_required
@role_required('client')
def feedback(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.user_id:
        flash('Not authorized.', 'danger')
        return redirect(url_for('client.dashboard'))

    if booking.status != 'Completed':
        flash('Feedback can only be submitted after the event is completed.', 'warning')
        return redirect(url_for('client.booking_detail', booking_id=booking_id))

    if request.method == 'POST':
        fb = Feedback(
            user_id=current_user.user_id,
            booking_id=booking.booking_id,
            rating=request.form.get('rating', type=int),
            comments=request.form.get('comments'),
        )
        db.session.add(fb)
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('client.booking_detail', booking_id=booking_id))

    return render_template('client/feedback.html', booking=booking)
