from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import math

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  #  CORS تنظیم  


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
    
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    details = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'details': self.details
        }  

def log_action(user_id, action, details=None):
    log = Log(user_id=user_id, action=action, details=details)
    db.session.add(log)
    db.session.commit()
  

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
        query = query.filter(User.age == age_filter)
    
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
def add_user():
    data = request.get_json()
    if not all(key in data for key in ['name', 'age', 'city', 'job']):
        return jsonify({'error': 'اطلاعات ناقص است'}), 400
    
    new_user = User(
        name=data['name'],
        age=data['age'],
        city=data['city'],
        job=data['job'],
        isActive = data.get('isActive', True)
    )

    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
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
    
    return jsonify(user.to_dict())


@app.route('/api/users/<int:user_id>/active', methods=['PATCH'])
def update_user_active(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if 'isActive' not in data:
        return jsonify({'error': 'مقدار isActive ارسال نشده است'}), 400
    user.isActive = data['isActive']
    db.session.commit()
    log_action(user_id, "change_active_status", f"set isActive to {data['isActive']}")
    return jsonify(user.to_dict())


@app.route('/api/users/<int:user_id>', methods=['PATCH'])
def patch_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if 'isActive' in data:
        user.isActive = data['isActive']
    db.session.commit()
    return jsonify(user.to_dict())

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'کاربر با موفقیت حذف شد'})

def initialize_database():
    db.create_all()
    
    if User.query.count() == 0:
        sample_users = [
            User(id=1, name="محمد امینی", age=28, city="تهران", job="برنامه‌نویس"),
            User(id=2, name="سارا محمدی", age=34, city="اصفهان", job="طراح"),
            User(id=3, name="علی رضایی", age=22, city="مشهد", job="مهندس"),
            User(id=4, name="مریم کریمی", age=31, city="تبریز", job="پزشک"),
            User(id=5, name="رضا حسینی", age=45, city="تهران", job="حسابدار"),
            User(id=6, name="زهرا نوری", age=29, city="شیراز", job="مدیر"),
            User(id=7, name="امیر قاسمی", age=37, city="اصفهان", job="معمار"),
            User(id=8, name="نیلوفر احمدی", age=26, city="تهران", job="طراح"),
            User(id=9, name="حسن فرهادی", age=33, city="مشهد", job="برنامه‌نویس"),
            User(id=10, name="فاطمه شریفی", age=24, city="تبریز", job="مهندس"),
            User(id=11, name="کامران جعفری", age=41, city="شیراز", job="مدیر"),
            User(id=12, name="شیما صادقی", age=38, city="تهران", job="حسابدار"),
        ]
        
        db.session.bulk_save_objects(sample_users)
        db.session.commit()

@app.route('/')
def home():
    return jsonify({"message": "به API کاربران خوش آمدید!"})

# مشاهده لاگ‌ها
@app.route('/api/logs', methods=['GET'])
def get_logs():
    logs = Log.query.order_by(Log.timestamp.desc()).all()
    return jsonify([log.to_dict() for log in logs])    

if __name__ == '__main__':
    with app.app_context():
        initialize_database()  
    app.run(debug=True)