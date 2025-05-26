from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
import math
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'my-very-secret-key'
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

# تنظیمات پایگاه داده
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)

# مدل کاربر
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    job = db.Column(db.String(100), nullable=False)
    isActive = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'city': self.city,
            'job': self.job,
            'isActive': self.isActive
        }

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    fullname = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default="user")
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'fullname': self.fullname,
            'role': self.role,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    affected_id = db.Column(db.Integer, nullable=True)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    details = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'affected_id': self.affected_id,
            'action': self.action,
            'timestamp': self.timestamp.isoformat() + 'Z' if self.timestamp else None,
            'details': self.details
        }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'ابتدا وارد شوید'}), 403
        return f(*args, **kwargs)
    return decorated_function

def log_action(user_id, action, affected_id=None, details=None):
    try:
        log = Log(
            user_id=user_id,
            action=action,
            affected_id=affected_id,
            details=details
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Logging failed: {e}")

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'نام کاربری و رمز عبور ضروری است'}), 400
    
    user = AdminUser.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        log_action(user.id, "login", details="ورود به سیستم")
        return jsonify({
            'message': 'ورود موفقیت‌آمیز بود',
            'user': user.to_dict()
        })
    return jsonify({'error': 'نام کاربری یا رمز عبور اشتباه است'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    if 'user_id' in session:
        user_id = session['user_id']
        session.clear()
        log_action(user_id, "logout", details="خروج از سیستم")
    return jsonify({'message': 'با موفقیت خارج شدید'})

@app.route('/api/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    name_filter = request.args.get('name', '')
    city_filter = request.args.get('city', '')
    job_filter = request.args.get('job', '')
    age_filter = request.args.get('age', '')
    
    query = User.query
    
    if name_filter:
        query = query.filter(User.name.ilike(f'%{name_filter}%'))
    if city_filter:
        query = query.filter(User.city.ilike(f'%{city_filter}%'))
    if job_filter:
        query = query.filter(User.job.ilike(f'%{job_filter}%'))
    if age_filter:
        query = query.filter(User.age.ilike(f"{age_filter}%"))
    
    total_items = query.count()
    total_pages = math.ceil(total_items / per_page)
    
    users = query.paginate(page=page, per_page=per_page)
    
    response = {
        'items': [user.to_dict() for user in users.items],
        'page': page,
        'per_page': per_page,
        'total_items': total_items,
        'total_pages': total_pages
    }
    
    return jsonify(response)

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@app.route('/api/users', methods=['POST'])
@login_required
def add_user():
    data = request.get_json()
    if not all(key in data for key in ['name', 'age', 'city', 'job']):
        return jsonify({'error': 'اطلاعات ناقص است'}), 400
    
    new_user = User(
        name=data['name'],
        age=data['age'],
        city=data['city'],
        job=data['job'],
        isActive=data.get('isActive', True)
    )

    db.session.add(new_user)
    db.session.commit()
    log_action(session['user_id'], "create_user", new_user.id, f"کاربر جدید با نام {new_user.name} ثبت شد")
    return jsonify(new_user.to_dict()), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'name' in data:
        user.name = data['name']
    if 'age' in data:
        user.age = data['age']
    if 'city' in data:
        user.city = data['city']
    if 'job' in data:
        user.job = data['job']
    
    db.session.commit()
    log_action(session['user_id'], "update_user", user_id, f"اطلاعات کاربر به‌روزرسانی شد")
    return jsonify(user.to_dict())

@app.route('/api/users/<int:user_id>', methods=['PATCH'])
def update_user_active(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if 'isActive' in data:
        user.isActive = data['isActive']
        db.session.commit()

        log_action(session.get('user_id', 0), "toggle_active", user_id, f"وضعیت کاربر به {'فعال' if user.isActive else 'غیرفعال'} تغییر کرد")
        return jsonify(user.to_dict())
    return jsonify({'error': 'پارامتر isActive ارسال نشده است'}), 400
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()
    
    log_action(session['user_id'], "delete_user", user_id, f"کاربر {user.name} حذف شد")
    return jsonify({'message': 'کاربر با موفقیت حذف شد'})

@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    logs = Log.query.order_by(Log.timestamp.desc()).all()
    return jsonify([log.to_dict() for log in logs])

def initialize_database():
    with app.app_context():
        db.create_all()
        
        if User.query.count() == 0:
            sample_users = [
                User(name="محمد امینی", age=28, city="تهران", job="برنامه‌نویس"),
                User(name="سارا محمدی", age=34, city="اصفهان", job="طراح"),
                User(name="علی رضایی", age=22, city="مشهد", job="مهندس"),
                User(name="مریم کریمی", age=31, city="تبریز", job="پزشک"),
                User(name="رضا حسینی", age=45, city="تهران", job="حسابدار"),
            ]
            
            db.session.bulk_save_objects(sample_users)
            db.session.commit()
        
        if AdminUser.query.count() == 0:
            admin = AdminUser(
                username="admin",
                fullname="مدیر سیستم"
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

@app.route('/')
def home():
    return jsonify({"message": "به API کاربران خوش آمدید!"})

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)