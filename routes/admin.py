from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from flask import abort
from models import db, User, AuditLog, Exam, Question

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated

# ── DASHBOARD ────────────────────────────────────────────────
@admin.route('/admin/dashboard')
@login_required
@admin_required
def dashboard():
    users = User.query.all()
    logs  = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(20).all()
    exams = Exam.query.all()
    return render_template('admin_dashboard.html', users=users, logs=logs, exams=exams)

# ── CREATE EXAM ──────────────────────────────────────────────
@admin.route('/admin/create_exam', methods=['GET', 'POST'])
@login_required
@admin_required
def create_exam():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        if not title:
            flash('Exam title is required.', 'danger')
            return render_template('create_exam.html')

        exam = Exam(title=title, created_by=current_user.id)
        db.session.add(exam)
        db.session.commit()
        flash(f'Exam "{title}" created! Now add questions.', 'success')
        return redirect(url_for('admin.add_question', exam_id=exam.id))

    return render_template('create_exam.html')

# ── ADD QUESTIONS ────────────────────────────────────────────
@admin.route('/admin/add_question/<int:exam_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def add_question(exam_id):
    exam = Exam.query.get_or_404(exam_id)

    if request.method == 'POST':
        q = Question(
            exam_id=exam_id,
            question_text=request.form.get('question_text'),
            option_a=request.form.get('option_a'),
            option_b=request.form.get('option_b'),
            option_c=request.form.get('option_c'),
            option_d=request.form.get('option_d'),
            correct_ans=request.form.get('correct_ans')
        )
        db.session.add(q)
        db.session.commit()
        flash('Question added!', 'success')

    questions = Question.query.filter_by(exam_id=exam_id).all()
    return render_template('add_question.html', exam=exam, questions=questions)
