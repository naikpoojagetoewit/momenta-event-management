import secrets
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User
from app.utils.email import send_registration_email, send_email

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

# In-memory store for password reset tokens (fine for a dev/demo project).
RESET_TOKENS = {}


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not all([name, email, phone, password, confirm_password]):
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        user = User(name=name, email=email, phone=phone, address=address, role='client')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        send_registration_email(user)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            if user.is_event_manager:
                return redirect(url_for('manager.dashboard'))
            if user.is_team_member:
                return redirect(url_for('team.dashboard'))
            return redirect(url_for('client.dashboard'))

        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = secrets.token_urlsafe(24)
            RESET_TOKENS[token] = {'user_id': user.user_id, 'created': datetime.utcnow()}
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            send_email(user.email, 'Momenta Password Reset',
                       f"<p>Click the link below to reset your password:</p>"
                       f"<p><a href='{reset_link}'>{reset_link}</a></p>"
                       f"<p>This link is valid for this session only.</p>")
        # Always show the same message so we don't leak which emails are registered.
        flash('If that email is registered, a reset link has been sent (check console/email).', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    data = RESET_TOKENS.get(token)
    if not data:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        if not password or password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.reset_password', token=token))

        user = User.query.get(data['user_id'])
        user.set_password(password)
        db.session.commit()
        RESET_TOKENS.pop(token, None)
        flash('Password reset successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)
