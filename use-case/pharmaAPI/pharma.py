from flask import Flask, render_template, jsonify
import psycopg2

app = Flask(__name__, static_url_path='/static')

# --- Database connection ---
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="parhma-db",
        user="postgres",
        port="5432",
        password="@qeadzc"
    )

# --- Home routes ---
@app.route('/')
def home():
    return render_template('clients.html')

@app.route('/clients')
def clients():
    return render_template('clients.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/orders')
def orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.invoice_id, i.invoice_number, i.invoice_date, 
               c.first_name || ' ' || c.last_name AS customer_name,
               i.total_amount, i.payment_status
        FROM invoices i
        JOIN customers c ON i.customer_id = c.customer_id
        ORDER BY i.invoice_date DESC
    """)
    orders = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('orders.html', orders=orders)

@app.route('/get_invoice_items/<int:invoice_id>')
def get_invoice_items(invoice_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.product_name, ii.quantity, ii.unit_price
        FROM invoice_items ii
        JOIN products p ON ii.product_id = p.product_id
        WHERE ii.invoice_id = %s
    """, (invoice_id,))
    
    items = [
        {
            "description": row[0],
            "quantity": row[1],
            "unit_price": float(row[2])
        }
        for row in cur.fetchall()
    ]
    
    cur.close()
    conn.close()
    return jsonify(items)

@app.route('/get_client_info/<int:invoice_id>')
def get_client_info(invoice_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.first_name, c.last_name, c.phone, c.email, c.address
        FROM invoices i
        JOIN customers c ON i.customer_id = c.customer_id
        WHERE i.invoice_id = %s
    """, (invoice_id,))
    
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return jsonify({
            "client_name": f"{row[0]} {row[1]}",
            "client_phone": row[2],
            "client_email": row[3],
            "client_address": row[4]
        })
    else:
        return jsonify({"error": "Client not found"}), 404

# --- Show all clients ---
@app.route('/show_clients')
def show_clients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT customer_id, first_name, last_name, phone, email, address, insurance_provider, insurance_number
        FROM customers
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    clients = [
        {
            "customer_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "phone": row[3],
            "email": row[4],
            "address": row[5],
            "insurance_provider": row[6],
            "insurance_number": row[7]
        }
        for row in rows
    ]
    return jsonify(clients)


# --- Show all orders (invoices) ---
@app.route('/show_orders')
def show_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.invoice_id, i.invoice_number, i.invoice_date, 
               c.first_name || ' ' || c.last_name AS customer_name,
               i.total_amount, i.payment_status
        FROM invoices i
        JOIN customers c ON i.customer_id = c.customer_id
        ORDER BY i.invoice_date DESC
    """)
    orders = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('show_orders.html', orders=orders)

# --- Show all products ---
@app.route('/show_products')
def show_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT product_id, product_code, product_name, 
               generic_name, strength, form, selling_price, tax_rate
        FROM products
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    products = [
        {
            "product_id": row[0],
            "product_code": row[1],
            "product_name": row[2],
            "generic_name": row[3],
            "strength": row[4],
            "form": row[5],
            "selling_price": str(row[6]),  # Convert Decimal to str if needed
            "tax_rate": str(row[7])
        }
        for row in rows
    ]

    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True, port=5004)
