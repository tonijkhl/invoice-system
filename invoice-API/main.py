from flask import Flask, request, jsonify, send_file
from werkzeug.security import generate_password_hash
import os
from datetime import datetime, timedelta
import secrets
from database import db
from functools import wraps
from invoice_template import generate_invoice
from werkzeug.security import check_password_hash
from message_queue import send_invoice_to_queue
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*"])

# Configuration
UPLOAD_FOLDER = 'logos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_api_key():
    return secrets.token_urlsafe(32)


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        
        if not api_key:
            return jsonify({"error": "API key is missing"}), 401
        
        conn = db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT user_id, company_name, email FROM users WHERE api_key = %s",
                    (api_key,)
                )
                user = cur.fetchone()
                
                if not user:
                    return jsonify({"error": "Invalid API key"}), 403
                
                # Create user_info dictionary
                user_info = {
                    'user_id': user[0],
                    'company_name': user[1],
                    'email': user[2]
                }
                
                # Pass user_info as first argument to the route
                return f(user_info, *args, **kwargs)
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            db.put_connection(conn)
    return decorated_function

# _________________________________MAIN ENDPOINTS __________________________________________________________________
@app.route('/new_user', methods=['POST'])
def new_user():
    data = request.json
    required = ['username', 'company_name', 'email', 'password']
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, company_name, email, password_hash, api_key) "
            "VALUES (%s, %s, %s, %s, %s) RETURNING user_id, username, email, api_key",
            (data['username'], data['company_name'], data['email'], 
             generate_password_hash(data['password']), generate_api_key())
        )
        user = cur.fetchone()
        conn.commit()
        return jsonify({
            "user_id": user[0],
            "username": user[1],
            "email": user[2],
            "api_key": user[3]
        }), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.put_connection(conn)

@app.route('/update_user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        conn = db.get_connection()
        cur = conn.cursor()
        
        # Build update query dynamically
        updates = []
        params = []
        if 'username' in data:
            updates.append("username = %s")
            params.append(data['username'])
        if 'company_name' in data:
            updates.append("company_name = %s")
            params.append(data['company_name'])
        if 'email' in data:
            updates.append("email = %s")
            params.append(data['email'])
        if 'password' in data:
            updates.append("password_hash = %s")
            params.append(generate_password_hash(data['password']))
        
        if not updates:
            return jsonify({"error": "Nothing to update"}), 400
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s RETURNING user_id, username, email"
        cur.execute(query, params)
        user = cur.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        conn.commit()
        return jsonify({
            "user_id": user[0],
            "username": user[1],
            "email": user[2]
        }), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.put_connection(conn)

@app.route('/show_user/<int:user_id>', methods=['GET'])
def show_user(user_id):
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, username, company_name, email, created_at "
            "FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({
            "user_id": user[0],
            "username": user[1],
            "company_name": user[2],
            "email": user[3],
            "created_at": user[4]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.put_connection(conn)

@app.route('/remove_user/<int:user_id>', methods=['DELETE'])
def remove_user(user_id):
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE user_id = %s RETURNING user_id", (user_id,))
        if not cur.fetchone():
            return jsonify({"error": "User not found"}), 404
        conn.commit()
        return jsonify({"message": "User deleted"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.put_connection(conn)

@app.route('/gen_new_api_key/<int:user_id>', methods=['POST'])
def gen_new_api_key(user_id):
    new_key = generate_api_key()
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET api_key = %s WHERE user_id = %s RETURNING api_key",
            (new_key, user_id))
        if not cur.fetchone():
            return jsonify({"error": "User not found"}), 404
        conn.commit()
        return jsonify({"api_key": new_key}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db.put_connection(conn)

def store_invoice_in_db(user_id, invoice_data):
    """Internal function to store invoice data in database"""
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        
        # Calculate total from items
        total_value = sum(item['quantity'] * item['unit_price'] for item in invoice_data['items'])
        
        # Insert into database
        cur.execute(
            "INSERT INTO invoices (user_id, invoice_date, total_value) "
            "VALUES (%s, %s, %s) RETURNING invoice_id",
            (user_id, invoice_data.get('invoice_date', datetime.now().date()), total_value)
        )
        invoice_id = cur.fetchone()[0]
        conn.commit()
        return invoice_id
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Failed to store invoice: {str(e)}")
        raise  # Re-raise the exception to handle in the main function
    finally:
        db.put_connection(conn)

@app.route('/generate_invoice', methods=['POST'])
@api_key_required
def create_invoice(user_info):
    try:
        data = request.json
        
        # Validate required fields
        if 'items' not in data:
            return jsonify({"error": "Missing required field: items"}), 400
        
        # Handle file upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and allowed_file(file.filename):
                filename = f"logo_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                data['logo_path'] = filepath
        
        # Set default values
        data.setdefault('invoice_number', f"INV-{datetime.now().strftime('%Y%m%d%H%M')}")
        data.setdefault('invoice_date', datetime.now().strftime('%Y-%m-%d'))
        data.setdefault('due_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        data.setdefault('tax_rate', 0)
        data.setdefault('business_name', user_info['company_name'])
        data.setdefault('business_email', user_info['email'])
        
        # Store invoice in database and get the generated ID
        invoice_id = store_invoice_in_db(user_info['user_id'], data)
        data['invoice_id'] = invoice_id  # Add to data for PDF generation
        
        # Generate PDF
        pdf_buffer = generate_invoice(data)

        # Send to queue (now with invoice_number)
        send_invoice_to_queue(
            email=data.get('client_email'),  # Ensure this field exists in request
            pdf_buffer=pdf_buffer,
            client_name=data.get('client_name')
        )

        # Reset buffer position after reading
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"invoice_{data['invoice_number']}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({"error": f"Invoice generation failed: {str(e)}"}), 500

@app.route('/metrics', methods=['POST'])
def get_metrics():
    try:
        data = request.json
        required = ['email', 'password']
        if not all(field in data for field in required):
            return jsonify({"error": "Missing required fields: email and password"}), 400

        conn = db.get_connection()
        try:
            with conn.cursor() as cur:
                # Get user by email
                cur.execute(
                    "SELECT user_id, password_hash, api_key FROM users WHERE email = %s",
                    (data['email'],)
                )
                user = cur.fetchone()
                
                if not user:
                    return jsonify({"error": "Invalid email or password"}), 401
                
                # Verify password
                if not check_password_hash(user[1], data['password']):
                    return jsonify({"error": "Invalid email or password"}), 401
                
                # Get invoice metrics
                cur.execute(
                    """SELECT 
                        COUNT(*) as total_invoices,
                        COALESCE(SUM(total_value), 0) as total_amount,
                        COALESCE(AVG(total_value), 0) as average_amount
                       FROM invoices 
                       WHERE user_id = %s""",
                    (user[0],)
                )
                metrics = cur.fetchone()
                
                return jsonify({
                    "api_key": user[2],
                    "total_invoices": metrics[0],
                    "total_amount": float(metrics[1]),
                    "average_amount": float(metrics[2])
                }), 200
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            db.put_connection(conn)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)