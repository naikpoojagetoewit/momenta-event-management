from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Booking, TeamMember, AssignedTask
from app.utils.decorators import role_required
from app.utils.email import send_status_update_email

manager_bp = Blueprint('manager', __name__, template_folder='../templates/manager')

STAGES = ['Planning', 'Decoration Started', 'Catering Ready', 'Photography Scheduled', 'Event Completed']


@manager_bp.route('/dashboard')
@login_required
@role_required('event_manager')
def dashboard():
    bookings = (Booking.query.filter_by(manager_id=current_user.user_id)
                .order_by(Booking.event_date).all())
    stats = {
        'total': len(bookings),
        'in_progress': sum(1 for b in bookings if b.status == 'In Progress'),
        'completed': sum(1 for b in bookings if b.status == 'Completed'),
    }
    return render_template('manager/dashboard.html', bookings=bookings, stats=stats)


@manager_bp.route('/event/<int:booking_id>', methods=['GET', 'POST'])
@login_required
@role_required('event_manager')
def event_detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.manager_id != current_user.user_id:
        flash('This event is not assigned to you.', 'danger')
        return redirect(url_for('manager.dashboard'))

    team_members = TeamMember.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_stage':
            booking.manager_stage = request.form.get('manager_stage')
            if booking.manager_stage == 'Event Completed':
                booking.status = 'Completed'
            elif booking.status == 'Assigned':
                booking.status = 'In Progress'
            db.session.commit()
            send_status_update_email(booking.client, booking)
            flash('Event status updated.', 'success')
        elif action == 'assign_task':
            task = AssignedTask(
                booking_id=booking.booking_id,
                member_id=request.form.get('member_id', type=int),
                task_description=request.form.get('task_description'),
            )
            db.session.add(task)
            db.session.commit()
            flash('Task assigned to team member.', 'success')
        return redirect(url_for('manager.event_detail', booking_id=booking_id))

    return render_template('manager/event_detail.html', booking=booking,
                            team_members=team_members, stages=STAGES)
