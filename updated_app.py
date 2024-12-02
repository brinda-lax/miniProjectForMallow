from flask import Flask, render_template, request, flash, url_for, redirect, session
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = "Admin@123"

# Utility function for database connection
def get_db_connection():
    conn = sql.connect('test.db')  # Ensure this path is correct
    conn.row_factory = sql.Row
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        user_data = {
            "name": request.form['name'],
            "email": request.form['email'],
            "phone": request.form['phone'],
            "address": request.form['address']
        }
        query = "INSERT INTO Users (name, email, phone, address) VALUES (?, ?, ?, ?)"
        try:
            with get_db_connection() as conn:
                conn.execute(query, tuple(user_data.values()))
                conn.commit()
            flash('User added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding user: {e}', 'error')
        return redirect(url_for('home'))
    return render_template('add_user.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_data = {
            "name": request.form['name'],
            "price_per_unit": float(request.form['price_per_unit']),
            "available_stocks": int(request.form['available_stocks']),
            "tax_percentage": float(request.form['tax_percentage'])
        }
        query = """
        INSERT INTO Products (name, price_per_unit, available_stocks, tax_percentage)
        VALUES (?, ?, ?, ?)
        """
        try:
            with get_db_connection() as conn:
                conn.execute(query, tuple(product_data.values()))
                conn.commit()
            flash('Product added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding product: {e}', 'error')
        return redirect(url_for('add_product'))
    return render_template('products.html')

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch users and products for dropdowns
    users = conn.execute('SELECT id, name FROM Users').fetchall()
    products = conn.execute('SELECT id, name, price_per_unit, tax_percentage FROM Products').fetchall()

    if request.method == 'POST':
        try:
            user_id = request.form['user_name']
            product_id = request.form['product_name']
            quantity = int(request.form['quantity'])
            paid_amount = float(request.form['paid_amount'])

            product_row = conn.execute(
                'SELECT price_per_unit, tax_percentage FROM Products WHERE id = ?',
                (product_id,)
            ).fetchone()

            if not product_row:
                flash(f"Product with ID {product_id} not found!", 'error')
                return redirect(url_for('purchase'))

            price_per_unit = product_row['price_per_unit']
            tax_percentage = product_row['tax_percentage']
            total_amount = (price_per_unit * quantity) * (1 + tax_percentage / 100)
            balance = max(0, total_amount - paid_amount)

            session.update({
                'user_id': user_id,
                'product_id': product_id,
                'quantity': quantity,
                'total_amount': total_amount,
                'paid_amount': paid_amount,
                'balance': balance
            })
            return redirect(url_for('generate_bill'))

        except Exception as e:
            flash(f"Error: {e}", 'error')
        finally:
            conn.close()

    return render_template('purchases.html', users=users, products=products)

@app.route('/generate_bill')
def generate_bill():
    if 'total_amount' in session:
        return render_template(
            'generate_bill.html',
            total_amount=session['total_amount'],
            paid_amount=session['paid_amount'],
            balance=session['balance']
        )
    flash("No purchase details found.", 'error')
    return redirect(url_for('purchase'))

@app.route('/get_user', methods=['GET', 'POST'])
def get_user():
    if request.method == 'POST':
        selected_username = request.form.get('user_name', type=str)
        if not selected_username:
            flash("User Name is required!", "error")
            return redirect(url_for('get_user'))

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM Users WHERE name = ?',
            (selected_username,)
        ).fetchone()
        conn.close()

        if user:
            session['user_name'] = selected_username
            return render_template('view_purchases.html')  # Redirect to view purchases page
        return "User doesn't exist"
    return render_template('get_user.html')

if __name__ == '__main__':
    app.run(debug=True)
