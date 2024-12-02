from flask import Flask,render_template,request,flash,url_for,redirect,session
from flask_mail import Mail, Message


import sqlite3 as sql

app=Flask(__name__)
app.secret_key="Admin@123"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Change this to your SMTP server
app.config['MAIL_PORT'] = 587  # For TLS
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = "abc@gmail.com"  # Your email address
app.config['MAIL_PASSWORD'] = 'Admin@123'  # Your email password

mail = Mail(app)

def send_confirmation_email(user_email):
    subject = "Welcome to Our Store"
    body = "Hello, \n\nYour account has been successfully created. Thank you for joining us!\n\nBest Regards,\nThe Store Team"
    
    msg = Message(subject, recipients=[user_email])
    msg.body = body
    
    try:
        mail.send(msg)
        print(f"Confirmation email sent to {user_email}")
    except Exception as e:
        print(f"Error sending email: {e}")


def get_db_connection():
    conn = sql.connect('test.db')  # Ensure this path is correct
    conn.row_factory = sql.Row
    return conn
def calculate_change(balance, denominations):
    result = {}
    
    # Loop through each denomination, starting from the largest
    for denom in denominations:
        if balance >= denom:
            # Calculate the number of notes/coins for this denomination
            num_denom = balance // denom
            result[denom] = num_denom
            # Subtract the equivalent amount from the balance
            balance -= num_denom * denom
    
    return result  # Return the calculated change breakdown
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/add_user',methods=['GET','POST'])
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
            with app.app_context():
                send_confirmation_email(user_data['email'])
       
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
            "available_stocks":int(request.form['available_stocks']),
            "tax_percentage": float(request.form['tax_percentage'])
        }
        query='''INSERT INTO Products (name, price_per_unit, available_stocks, tax_percentage)
                VALUES (?, ?, ?, ?)'''
        # Establish connection with the database
        try: 
            with get_db_connection() as conn:
              
                conn.execute(query, tuple(product_data.values()))
                conn.commit()
        
            # Flash a success message
            flash('Product added successfully!', 'success')

        except Exception as e:
            # Flash an error message if there's an issue
            flash(f'Error adding product: {e}', 'error')
        return redirect(url_for('add_product'))  # Redirect to home page after success
    return render_template('products.html')
   
@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch users and products for dropdowns
    cursor.execute('SELECT id, name FROM Users')
    users = cursor.fetchall()
    cursor.execute('SELECT id, name, price_per_unit, tax_percentage FROM Products')
    products = cursor.fetchall()

    if request.method == 'POST':
        try:
            # Get form data
            user_id = request.form['user_name']
            product_id = request.form['product_name']
            quantity = int(request.form['quantity'])
            paid_amount = float(request.form['paid_amount'])

            # Fetch product details by product_id
            cursor.execute('SELECT id, price_per_unit, tax_percentage FROM Products WHERE id = ?', (product_id,))
            product_row = cursor.fetchone()
            if product_row:
                price_per_unit = product_row['price_per_unit']
                tax_percentage = product_row['tax_percentage']
            else:
                flash(f"Product with ID {product_id} not found!", 'error')
                return redirect(url_for('purchase'))

            # Calculate total amount and balance
            total_amount = (price_per_unit * quantity) * (1 + tax_percentage / 100)
            balance = max(0, total_amount - paid_amount)

            # Store bill details in session
            session['user_id'] = user_id
            session['product_id'] = product_id
            session['quantity'] = quantity
            session['total_amount'] = total_amount
            session['paid_amount'] = paid_amount
            session['balance'] = balance

            # Commit transaction
            conn.commit()

            # Redirect to the generate bill page
            return redirect(url_for('generate_bill'))

        except Exception as e:
            flash(f"Error: {e}", 'error')
        finally:
            conn.close()

    return render_template('purchases.html', users=users, products=products)

@app.route('/generate_bill')
def generate_bill():
    # Fetch bill details from the session
    if 'total_amount' in session:
        total_amount = session['total_amount']
        paid_amount = session['paid_amount']
        balance = session['balance']
        # You can add more details as needed
        available_denominations = [100, 50, 20, 10, 5, 1]

        # Calculate the denominations needed for the balance
        change = calculate_change(balance, available_denominations)
        
        return render_template('generate_bill.html', 
                               total_amount=total_amount, 
                               paid_amount=paid_amount, 
                               balance=balance,
                               change=change)
    else:
        flash("No purchase details found.", 'error')
        return redirect(url_for('purchase'))

    
@app.route('/get_user', methods=['GET','POST'])
def get_user():
    if request.method == 'POST':
        # Get the username from the form
        selected_username = request.form.get('user_name', type=str)

        if not selected_username:
            flash("User Name is required!", "error")
            return redirect(url_for('get_user'))

        # Check if the user exists in the database
        conn = sql.connect('test.db')
        conn.row_factory = sql.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE name = ?', (selected_username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            # If user exists, store the username in session and proceed
            session['user_name'] = selected_username
            return render_template('view_purchases.html')  # Redirect to view purchases page
        else:
            # If user does not exist, show an error message and stay on the same page
            #flash("User does not exist!", "error")
            return "User doesnt exists"

    
    return render_template('get_user.html')




if __name__=='__main__':
    
    app.run(debug=True)
