from flask import Flask
from models import db
from flask_login import LoginManager
from config import Config
import bcrypt

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Login manager handles sessions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Redirect here if not logged in

from models import User

@login_manager.user_loader
def load_user(user_id):
   return db.session.get(User, int(user_id))

# Register route blueprints
from routes.auth import auth
from routes.student import student
from routes.admin import admin

app.register_blueprint(auth)
app.register_blueprint(student)
app.register_blueprint(admin)

# Create all tables and a default admin user on first run
with app.app_context():
    db.create_all()

    # Create default admin if none exists
    if not User.query.filter_by(username='admin').first():
        hashed = bcrypt.hashpw('Admin@1234'.encode('utf-8'), bcrypt.gensalt())
        admin_user = User(
            username='admin',
            email='admin@exam.com',
            password_hash=hashed.decode('utf-8'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Default admin created — username: admin, password: Admin@1234")

if __name__ == '__main__':
    app.run(debug=True)