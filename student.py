from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Exam, Question, Submission, AuditLog
import json, random

student = Blueprint('student', __name__)

def log_action(action, user_id=None, details=''):
    from flask import request as req
    entry = AuditLog(
        user_id=user_id,
        action=action,
        ip_address=req.remote_addr,
        details=details
    )
    db.session.add(entry)
    db.session.commit()

# ── EXAM HOME ────────────────────────────────────────────────
@student.route('/exam')
@login_required
def exam_home():
    exams = Exam.query.filter_by(is_active=True).all()
    return render_template('student_exam.html', exams=exams, user=current_user)

# ── TAKE EXAM ────────────────────────────────────────────────
@student.route('/exam/<int:exam_id>', methods=['GET', 'POST'])
@login_required
def take_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)

    # Prevent re-submission
    already = Submission.query.filter_by(
        user_id=current_user.id, exam_id=exam_id).first()
    if already:
        flash('You have already submitted this exam.', 'warning')
        return redirect(url_for('student.exam_home'))

    questions = Question.query.filter_by(exam_id=exam_id).all()
    random.shuffle(questions)  # Randomize order — security control

    if request.method == 'POST':
        answers = {}
        score   = 0

        for q in questions:
            ans = request.form.get(f'q_{q.id}', '')
            answers[str(q.id)] = ans
            if ans == q.correct_ans:
                score += 1

        submission = Submission(
            user_id=current_user.id,
            exam_id=exam_id,
            answers=json.dumps(answers),
            score=score
        )
        db.session.add(submission)
        db.session.commit()

        log_action('EXAM_SUBMITTED', current_user.id,
                   f'Exam: {exam.title} | Score: {score}/{len(questions)}')

        flash(f'✅ Submitted! Your score: {score} / {len(questions)}', 'success')
        return redirect(url_for('student.exam_home'))

    return render_template('take_exam.html', exam=exam, questions=questions)