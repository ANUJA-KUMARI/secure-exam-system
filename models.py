from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role          = db.Column(db.String(20), default='student')  # student / admin
    failed_logins = db.Column(db.Integer, default=0)
    locked_until  = db.Column(db.DateTime, nullable=True)

class Exam(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active  = db.Column(db.Boolean, default=True)
    questions  = db.relationship('Question', backref='exam', lazy=True)

class Question(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    exam_id       = db.Column(db.Integer, db.ForeignKey('exam.id'))
    question_text = db.Column(db.Text, nullable=False)
    option_a      = db.Column(db.String(200))
    option_b      = db.Column(db.String(200))
    option_c      = db.Column(db.String(200))
    option_d      = db.Column(db.String(200))
    correct_ans   = db.Column(db.String(1))

class Submission(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'))
    exam_id      = db.Column(db.Integer, db.ForeignKey('exam.id'))
    answers      = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    score        = db.Column(db.Integer)

class AuditLog(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, nullable=True)
    action     = db.Column(db.String(200))
    ip_address = db.Column(db.String(50))
    timestamp  = db.Column(db.DateTime, default=datetime.utcnow)
    details    = db.Column(db.Text)