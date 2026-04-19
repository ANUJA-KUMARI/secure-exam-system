from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required
from models import db, User, AuditLog
from datetime import datetime, timedelta
import bcrypt

auth = Blueprint('auth', __name__)

# ── HELPER: Save every action to audit log ──────────────────
def log_action(action, user_id=None, details=''):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        ip_address=request.remote_addr,
        details=details
    )
    db.session.add(entry)
    db.session.commit()

# ── LOGIN ROUTE ─────────────────────────────────────────────
@auth.route('/', methods=['GET', 'POST'])
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Basic input validation — never trust user input
        if not username or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()

        # Check if account is locked (brute force protection)
        if user and user.locked_until and datetime.utcnow() < user.locked_until:
            remaining = (user.locked_until - datetime.utcnow()).seconds // 60
            flash(f'Account locked. Try again in {remaining} minutes.', 'danger')
            log_action('LOGIN_BLOCKED', user.id, f'Account locked — IP: {request.remote_addr}')
            return render_template('login.html')

        # Verify password using bcrypt
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # SUCCESS — reset failed attempts
            user.failed_logins = 0
            user.locked_until = None
            db.session.commit()

            login_user(user)
            log_action('LOGIN_SUCCESS', user.id, f'Role: {user.role}')

            # Redirect based on role (Role-Based Access Control)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('student.exam_home'))

        else:
            # FAILED LOGIN — increment counter
            if user:
                user.failed_logins += 1

                # Lock account after 5 failed attempts (30 minutes)
                if user.failed_logins >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                    db.session.commit()
                    flash('Too many failed attempts. Account locked for 30 minutes.', 'danger')
                    log_action('ACCOUNT_LOCKED', user.id, 'Locked after 5 failed attempts')
                    return render_template('login.html')

                db.session.commit()
                log_action('LOGIN_FAIL', user.id, f'Failed attempt #{user.failed_logins}')

            else:
                # Username doesn't exist — log it but show same message
                # (never reveal if username exists or not — prevents enumeration)
                log_action('LOGIN_FAIL_UNKNOWN', details=f'Unknown username tried: {username}')

            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

# ── LOGOUT ROUTE ─────────────────────────────────────────────
@auth.route('/logout')
@login_required
def logout():
    from flask_login import current_user
    log_action('LOGOUT', current_user.id)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

# ── REGISTER ROUTE ───────────────────────────────────────────
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Input validation
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('register.html')

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')

        # Hash password before storing — NEVER store plain text
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        new_user = User(
            username=username,
            email=email,
            password_hash=hashed.decode('utf-8'),
            role='student'
        )
        db.session.add(new_user)
        db.session.commit()

        log_action('REGISTER_SUCCESS', new_user.id, f'New student: {username}')
        flash('Account created! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')