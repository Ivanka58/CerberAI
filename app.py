import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import db

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DEV_PASSWORD = os.environ.get('DEV_PASSWORD', '040111')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/api/auth/telegram', methods=['POST'])
def auth_telegram():
    data = request.json
    code = data.get('code')
    unique_link = data.get('unique_link')
    
    if not code or not unique_link:
        return jsonify({'success': False, 'error': 'Missing code or unique_link'}), 400
    
    verified = db.verify_telegram_code(code, unique_link)
    
    if not verified:
        return jsonify({'success': False, 'error': 'Invalid or expired code'}), 400
    
    telegram_data = data.get('telegram_data', {})
    telegram_id = telegram_data.get('id')
    
    if not telegram_id:
        return jsonify({'success': False, 'error': 'No telegram data'}), 400
    
    user = db.get_user_by_telegram_id(telegram_id)
    
    if not user:
        user = db.create_user_telegram(
            telegram_id=telegram_id,
            username=telegram_data.get('username'),
            first_name=telegram_data.get('first_name'),
            last_name=telegram_data.get('last_name'),
            avatar_url=telegram_data.get('photo_url')
        )
    
    db.update_user_days_count(user['id'])
    
    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'username': user['username'] or user['first_name'],
            'avatar': user['avatar_url'],
            'days_count': user['days_count']
        }
    })

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    stats = db.get_user_stats(user_id)
    balance = db.get_balance(user_id)
    
    return jsonify({
        'user': {
            'id': user['id'],
            'username': user['username'] or user['first_name'],
            'avatar': user['avatar_url'],
            'days_count': user['days_count'],
            'stats': stats,
            'balance': balance['balance'] if balance else 0
        }
    })

@app.route('/api/facts/<int:user_id>', methods=['GET', 'POST'])
def handle_facts(user_id):
    if request.method == 'GET':
        facts = db.get_facts(user_id)
        return jsonify({'facts': facts})
    
    data = request.json
    key = data.get('key')
    value = data.get('value')
    category = data.get('category', 'general')
    
    db.save_fact(user_id, key, value, category)
    return jsonify({'success': True})

if __name__ == '__main__':
    db.init_database()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
