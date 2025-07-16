from flask import Flask, render_template
from flask import render_template, session, redirect, url_for, flash, jsonify
from werkzeug.security import check_password_hash
from database import db
from flask import request
from datetime import timedelta
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your-very-secure-secret-key-123'  # Change this!
app.config.update(
    SESSION_COOKIE_SECURE=False,  # True in production (requires HTTPS)
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',  # Helps prevent CSRF
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)  # Session expiration
)

CORS(app, 
    supports_credentials=True,
    resources={
        r"/*": {
            "origins": ["http://localhost:5001"],  # frontend origin
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    }
)
@app.route('/')
def home():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    return redirect(url_for('sign_in'))

@app.route('/sign_in')
def sign_in():
    return render_template('sign_in.html')

@app.route('/user_info')
def user():
    return render_template('user_info.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('sign_in'))
@app.route('/check_session', methods=['GET'])
def check_session():
    if 'user' in session:
        return jsonify({
            'logged_in': True,
            'user': session['user']
        }), 200
    return jsonify({'logged_in': False}), 401

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, username, email, password_hash, api_key, company_name FROM users WHERE email = %s",
            (email,)
        )
        user = cur.fetchone()
        if not user or not check_password_hash(user[3], password):
            return jsonify({'error': 'Invalid credentials'}), 401

        session['user'] = {
            'user_id': user[0],
            'username': user[1],
            'email': user[2],
            'api_key': user[4],
            'company_name': user[5]
        }

        return jsonify({'message': 'Login successful'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.put_connection(conn)

@app.route('/current_user', methods=['GET'])
def current_user():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify(session['user']), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)







