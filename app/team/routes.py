import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import TeamMember, AssignedTask

team_bp = Blueprint('team', __name__, template_folder='../templates/team')


def _current_member():
    return TeamMember.query.filter_by(user_id=current_user.user_id).first()


@team_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_team_member:
        flash('Not authorized.', 'danger')
        return redirect(url_for('main.home'))

    member = _current_member()
    tasks = AssignedTask.query.filter_by(member_id=member.member_id).all() if member else []
    return render_template('team/dashboard.html', member=member, tasks=tasks)


@team_bp.route('/task/<int:task_id>/update', methods=['POST'])
@login_required
def update_task(task_id):
    member = _current_member()
    task = AssignedTask.query.get_or_404(task_id)
    if not member or task.member_id != member.member_id:
        flash('Not authorized.', 'danger')
        return redirect(url_for('team.dashboard'))

    task.task_status = request.form.get('task_status', task.task_status)

    file = request.files.get('proof_file')
    if file and file.filename:
        filename = secure_filename(f"task_{task.task_id}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        task.file_path = f"uploads/{filename}"

    db.session.commit()
    flash('Task updated.', 'success')
    return redirect(url_for('team.dashboard'))


@team_bp.route('/attendance', methods=['POST'])
@login_required
def mark_attendance():
    # Lightweight attendance marker - stores today's check-in on the session/flash for demo purposes.
    flash('Attendance marked for today.', 'success')
    return redirect(url_for('team.dashboard'))
