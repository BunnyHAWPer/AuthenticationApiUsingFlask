from flask import Flask, request, jsonify, send_from_directory
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
import os
import bcrypt

app = Flask(__name__)
DATABASE_NAME = "your_database_name"
app.config['MONGO_URI'] = f'mongodb://localhost:27017/{DATABASE_NAME}'
mongo = PyMongo(app)

UPLOAD_FOLDER = 'uploads/profile_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploads/profile_images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['POST'])
def register():
    if request.method != 'POST':
        return jsonify({'success': False, 'message': 'Method not allowed'}), 405
    
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    profile_image = request.files.get('profile_image')

    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'Name, email, and password are required'}), 400

    if mongo.db.users.find_one({'email': email}):
        return jsonify({'success': False, 'message': 'Email already exists'}), 400

    if profile_image and allowed_file(profile_image.filename):
        filename = secure_filename(profile_image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_image.save(filepath)
    else:
        filepath = None

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user_data = {
        'name': name,
        'email': email,
        'password': hashed_password,
        'profile_image': filepath
    }

    mongo.db.users.insert_one(user_data)

    return jsonify({'success': True, 'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    if request.method != 'POST':
        return jsonify({'success': False, 'message': 'Method not allowed'}), 405
    
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400

    user = mongo.db.users.find_one({'email': email})

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        user_details = {
            'name': user.get('name'),
            'email': user.get('email'),
            'profile_image': user.get('profile_image'),
        }
        return jsonify({'success': True, 'message': 'Login successful', 'user': user_details}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401


if __name__ == '__main__':
    app.run(debug=True)
