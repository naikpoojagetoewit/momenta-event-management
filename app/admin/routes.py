from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models import User, EventType, Service, Booking, Payment, TeamMember, Feedback
from app.utils.decorators import role_required
from app.utils.email import send_status_update_email

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')


@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    total_users = User.query.filter_by(role='client').count()
    total_events = EventType.query.count()
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter_by(
        payment_status='Success').scalar()
    active_events = Booking.query.filter(Booking.status.in_(['Approved', 'Assigned', 'In Progress'])).count()

    # Grouped in Python (rather than func.strftime, which is SQLite-only) so this
    # works unchanged whether the project is running on SQLite or PostgreSQL.
    successful_payments = Payment.query.filter_by(payment_status='Success').order_by(Payment.created_at).all()
    monthly_totals = {}
    for p in successful_payments:
        key = p.created_at.strftime('%Y-%m')
        monthly_totals[key] = monthly_totals.get(key, 0) + p.amount
    revenue_by_month = list(monthly_totals.items())
    popular_events = (
        db.session.query(EventType.event_name, func.count(Booking.booking_id).label('cnt'))
        .join(Booking, Booking.event_id == EventType.event_id)
        .group_by(EventType.event_name).order_by(func.count(Booking.booking_id).desc()).limit(5).all()
    )
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(8).all()

    return render_template('admin/dashboard.html',
                            total_users=total_users, total_events=total_events,
                            total_bookings=total_bookings, total_revenue=total_revenue,
                            active_events=active_events,
                            revenue_labels=[r[0] for r in revenue_by_month],
                            revenue_values=[float(r[1]) for r in revenue_by_month],
                            popular_labels=[p[0] for p in popular_events],
                            popular_values=[p[1] for p in popular_events],
                            recent_bookings=recent_bookings)


# ---------------- User Management ----------------
@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/add', methods=['POST'])
@login_required
@role_required('admin')
def add_user():
    email = request.form.get('email', '').strip().lower()
    if User.query.filter_by(email=email).first():
        flash('Email already exists.', 'danger')
        return redirect(url_for('admin.users'))
    user = User(
        name=request.form.get('name'), email=email,
        phone=request.form.get('phone'), address=request.form.get('address'),
        role=request.form.get('role', 'client'),
    )
    user.set_password(request.form.get('password') or 'momenta123')
    db.session.add(user)
    db.session.commit()
    flash('User added successfully.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    user.name = request.form.get('name')
    user.phone = request.form.get('phone')
    user.address = request.form.get('address')
    user.role = request.form.get('role')
    db.session.commit()
    flash('User updated.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.user_id == current_user.user_id:
        flash("You can't delete your own account.", 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted.', 'success')
    return redirect(url_for('admin.users'))


# ---------------- Event Management ----------------
@admin_bp.route('/events')
@login_required
@role_required('admin')
def events():
    all_events = EventType.query.all()
    return render_template('admin/events.html', events=all_events)


@admin_bp.route('/events/add', methods=['POST'])
@login_required
@role_required('admin')
def add_event():
    event = EventType(
        event_name=request.form.get('event_name'),
        category=request.form.get('category'),
        description=request.form.get('description'),
        base_price=request.form.get('base_price', type=float, default=0),
    )
    db.session.add(event)
    db.session.commit()
    flash('Event added.', 'success')
    return redirect(url_for('admin.events'))


@admin_bp.route('/events/<int:event_id>/edit', methods=['POST'])
@login_required
@role_required('admin')
def edit_event(event_id):
    event = EventType.query.get_or_404(event_id)
    event.event_name = request.form.get('event_name')
    event.category = request.form.get('category')
    event.description = request.form.get('description')
    event.base_price = request.form.get('base_price', type=float, default=0)
    event.is_active = bool(request.form.get('is_active'))
    db.session.commit()
    flash('Event updated.', 'success')
    return redirect(url_for('admin.events'))


@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_event(event_id):
    event = EventType.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted.', 'success')
    return redirect(url_for('admin.events'))


# ---------------- Service Management ----------------
@admin_bp.route('/services')
@login_required
@role_required('admin')
def services():
    all_services = Service.query.all()
    return render_template('admin/services.html', services=all_services)


@admin_bp.route('/services/add', methods=['POST'])
@login_required
@role_required('admin')
def add_service():
    service = Service(
        service_name=request.form.get('service_name'),
        category=request.form.get('category'),
        tier=request.form.get('tier'),
        price=request.form.get('price', type=float, default=0),
        unit=request.form.get('unit', 'per event'),
        description=request.form.get('description'),
    )
    db.session.add(service)
    db.session.commit()
    flash('Service added.', 'success')
    return redirect(url_for('admin.services'))


@admin_bp.route('/services/<int:service_id>/edit', methods=['POST'])
@login_required
@role_required('admin')
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    service.service_name = request.form.get('service_name')
    service.category = request.form.get('category')
    service.tier = request.form.get('tier')
    service.price = request.form.get('price', type=float, default=0)
    service.unit = request.form.get('unit', 'per event')
    service.is_active = bool(request.form.get('is_active'))
    db.session.commit()
    flash('Service updated.', 'success')
    return redirect(url_for('admin.services'))


@admin_bp.route('/services/<int:service_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash('Service removed.', 'success')
    return redirect(url_for('admin.services'))


# ---------------- Booking Management ----------------
@admin_bp.route('/bookings')
@login_required
@role_required('admin')
def bookings():
    status_filter = request.args.get('status')
    query = Booking.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    all_bookings = query.order_by(Booking.created_at.desc()).all()
    managers = User.query.filter_by(role='event_manager').all()
    return render_template('admin/bookings.html', bookings=all_bookings, managers=managers,
                            status_filter=status_filter)


@admin_bp.route('/bookings/<int:booking_id>/approve', methods=['POST'])
@login_required
@role_required('admin')
def approve_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'Approved'
    db.session.commit()
    send_status_update_email(booking.client, booking)
    flash('Booking approved.', 'success')
    return redirect(url_for('admin.bookings'))


@admin_bp.route('/bookings/<int:booking_id>/reject', methods=['POST'])
@login_required
@role_required('admin')
def reject_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'Rejected'
    db.session.commit()
    send_status_update_email(booking.client, booking)
    flash('Booking rejected.', 'info')
    return redirect(url_for('admin.bookings'))


@admin_bp.route('/bookings/<int:booking_id>/assign', methods=['POST'])
@login_required
@role_required('admin')
def assign_manager(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.manager_id = request.form.get('manager_id', type=int)
    booking.status = 'Assigned'
    db.session.commit()
    send_status_update_email(booking.client, booking)
    flash('Event manager assigned.', 'success')
    return redirect(url_for('admin.bookings'))


# ---------------- Team Management ----------------
@admin_bp.route('/team')
@login_required
@role_required('admin')
def team():
    members = TeamMember.query.all()
    return render_template('admin/team.html', members=members)


@admin_bp.route('/team/add', methods=['POST'])
@login_required
@role_required('admin')
def add_team_member():
    member = TeamMember(
        name=request.form.get('name'),
        role=request.form.get('role'),
        phone=request.form.get('phone'),
    )
    db.session.add(member)
    db.session.commit()
    flash('Team member added.', 'success')
    return redirect(url_for('admin.team'))


@admin_bp.route('/team/<int:member_id>/edit', methods=['POST'])
@login_required
@role_required('admin')
def edit_team_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    member.name = request.form.get('name')
    member.role = request.form.get('role')
    member.phone = request.form.get('phone')
    member.is_active = bool(request.form.get('is_active'))
    db.session.commit()
    flash('Team member updated.', 'success')
    return redirect(url_for('admin.team'))


@admin_bp.route('/team/<int:member_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_team_member(member_id):
    member = TeamMember.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash('Team member removed.', 'success')
    return redirect(url_for('admin.team'))


# ---------------- Reports ----------------
@admin_bp.route('/reports')
@login_required
@role_required('admin')
def reports():
    today = datetime.utcnow().date()
    daily = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.payment_status == 'Success',
        func.date(Payment.created_at) == today,
    ).scalar()

    month_start = today.replace(day=1)
    monthly = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.payment_status == 'Success',
        Payment.created_at >= month_start,
    ).scalar()

    year_start = today.replace(month=1, day=1)
    annual = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).filter(
        Payment.payment_status == 'Success',
        Payment.created_at >= year_start,
    ).scalar()

    return render_template('admin/reports.html', daily=daily, monthly=monthly, annual=annual)
