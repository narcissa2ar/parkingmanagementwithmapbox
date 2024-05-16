
import sqlite3
import secrets
import uuid

from flask import Flask, render_template, request, redirect, session
from flask import  url_for
from datetime import datetime
from flask import Flask, request

from flask_login import login_required 
import random
import string
import paypalrestsdk
def generate_transaction_id():
    transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return transaction_id

app = Flask(__name__)
paypalrestsdk.configure({
  "mode": "sandbox",  # sandbox or live
  "client_id": "AUnIYB3nQtHNe8G8Lv_47n44xNOri87qWXZ5ZVbstuhaSECu8fgI3xUOeDgiMLK-hsRtE4kOHVfqRPlc",
  "client_secret": "ELT2xeFiaAMMB3CzPEKjJRtQhNDwY1IF9cyoB8dXoaID_MbpCO8fSo_a0vhYs2W8XcYWdeo6Of--jT_L"
})
app.config['DATABASE'] = 'C:/Users/HP/Documents/parkingproject/ware.db'
app.secret_key = secrets.token_hex(16)  # Generate a secret key for sessions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adminLogin')
def adminlogin():
    return render_template('parking lot administrator login.html')

@app.route('/adminportal')
def adminportal():
    return render_template('adminportal.html')
@app.route('/Loginr')
def loginr():
    return render_template('user.html')
@app.route('/useroradmin')
def useroradmin():
    return render_template('useroradmin.html')
@app.route('/loginoregister')
def loginoregister():
    return render_template('loginoregister.html')


@app.route('/success_payment')
def successpage():
    return render_template('payment_success.html')

@app.route('/login_page')
def login_page():
    return render_template('login page.html')

@app.route('/admindash', methods=['POST'])
def admindash():
    # Get the email and password from the form
    email = request.form['email']
    password = request.form['password']

    # Validate the credentials (this is just a basic example, you should hash passwords and use proper authentication)
    if email == 'admin@example.com' and password == 'adminpassword':
        return render_template('administrator dashboard.html')
    else:
        # Invalid credentials, redirect back to login page
        return redirect(url_for('/adminLogin'))

@app.route('/loginUser')
def login_user():
    return render_template('user login.html')

@app.route('/registerUser')
def register_user_in():
    return render_template('user register.html')

    
@app.route('/booking_details')
def booking_details():
    # Retrieve booking details from the database
    db = sqlite3.connect(app.config['DATABASE'])
    cursor = db.cursor()
    cursor.execute("SELECT * FROM booking")
    bookings = cursor.fetchall()
    db.close()

    # Pass bookings to the template
    return render_template('administrator dashboard.html', bookings=bookings)
    
    
 # Login route for parking lot managers
@app.route('/loginM', methods=['GET', 'POST'])
def manager_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to the database
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()

        # Check if email and password match a manager in the manager table
        cursor.execute("SELECT * FROM manager WHERE email=? AND password=?", (email, password))
        manager = cursor.fetchone()

        if manager:
            # Redirect based on the email and password combination
            if email == 'muser@example.com' and password == 'password2':
                return render_template('manager dashboard.html')
            elif email == 'm2user@example.com' and password == 'password':
                return render_template('manager dashboard2.html')
            else:
                return "Invalid email or password combination for manager."

        # If login fails, render the mlogin.html template
        return render_template('mlogin.html')

    # For GET requests, render the mlogin.html template
    return render_template('mlogin.html')




@app.route('/payment_failed')
def payment_failed():
    return render_template('payment_fail.html')
@app.route('/logout')
def logout():
    # Delete email from user_session table
    db = sqlite3.connect(app.config['DATABASE'])
    cursor = db.cursor()
    cursor.execute("DELETE FROM user_session WHERE email=?", (session.get('email'),))
    db.commit()
    db.close()

    # Clear session data
    session.clear()

    # Redirect to the index page
    return redirect(url_for('index'))






@app.route('/loginmdash')
def dashm():
    return render_template('manager dashboard.html')

# Route to display booking information
@app.route('/booking_info1')
def booking_info1():
    # Connect to the database
    db = sqlite3.connect(app.config['DATABASE'])
    cursor = db.cursor()

    # Fetch booking information from the database
    cursor.execute("SELECT * FROM booking WHERE location_name ='Day'")
    bookings = cursor.fetchall()

    # Close the database connection
    db.close()

    return render_template('booking_info.html', bookings=bookings)



@app.route('/payment', methods=['GET', 'POST'])
def payment_page():
    # Get the location name from the request parameters or session
    location_name = request.form.get('location_name')

    # Fetch price from the database based on location name
    db = sqlite3.connect(app.config['DATABASE'])
    cursor = db.cursor()
    cursor.execute("SELECT price FROM Location WHERE loc_name = ?", (location_name,))
    price = cursor.fetchone()[0]  # Assuming price is fetched correctly

    # Fetch email from the user_session table
    cursor.execute("SELECT email FROM user_session")
    email = cursor.fetchone()[0]  # Assuming email is fetched correctly

    # Render the payment.html template and pass location name, price, and email to the template context
    return render_template('payment.html', location_name=location_name, price=price, email=email)

def generate_booking_id():
    return f"{datetime.now().isoformat('_')}-{str(uuid.uuid4())[:8]}"
from flask import redirect, url_for, render_template

@app.route('/payment/paypal', methods=['POST'])
def paypal_payment():
    if request.method == 'POST':
        # Get payment details from the form
        email = request.form['email']
        location_name = request.form['location_name']
        date_in = request.form['date_in']
        time_in = request.form['time_in']
        date_out = request.form['date_out']
        time_out = request.form['time_out']
        payment_amount = float(request.form['payment_amount'])
        currency = request.form['currency']

        # Generate booking ID
        booking_id = generate_booking_id()

        # Insert booking details into the database
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()
        cursor.execute("INSERT INTO booking (booking_id, email, time_in, time_out, date_in, date_out, location_name, payment_amount, currency, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (booking_id, email, time_in, time_out, date_in, date_out, location_name, payment_amount, currency, 'pending'))
        db.commit()

        # Generate transaction ID
        transaction_id = generate_transaction_id()

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "http://localhost:5000/payment/execute",
                "cancel_url": "http://localhost:5000/payment/cancel"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": location_name,
                        "sku": "item",
                        "price": payment_amount,
                        "currency": currency,
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": payment_amount,
                    "currency": currency
                },
                "description": "Parking Reservation"
            }]
        })

        if payment.create():
            # Store payment ID and booking ID in session
            session['payment_id'] = payment.id
            session['booking_id'] = booking_id

            # Store transaction in the database
            cursor.execute("INSERT INTO transaction1 (transaction_id, booking_id, payment_id, payer_email, payee_email, amount, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (transaction_id, booking_id, payment.id, email, 'business_owner@example.com', payment_amount, 'pending'))
            db.commit()
            db.close()

            # Redirect to approval URL
            for link in payment.links:
                if link.method == "REDIRECT":
                    return redirect(link.href)
        else:
            return render_template('payment_fail.html', error=payment.error)

@app.route('/payment/execute', methods=['GET', 'POST'])
def execute_payment():
    if request.method == 'GET' and 'paymentId' in request.args and 'PayerID' in request.args:
        payment_id = request.args.get('paymentId')
        payer_id = request.args.get('PayerID')

        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            # Update transaction status to completed
            db = sqlite3.connect(app.config['DATABASE'])
            cursor = db.cursor()
            
            # Update the transaction status to completed
            cursor.execute("UPDATE transaction1 SET status = ? WHERE payment_id = ?", ('completed', payment_id))
            db.commit()

            # Get booking_id associated with the transaction_id
            cursor.execute("SELECT booking_id FROM transaction1 WHERE payment_id = ?", (payment_id,))
            booking_id = cursor.fetchone()[0]

            # Update booking status to completed
            cursor.execute("UPDATE booking SET status = ? WHERE booking_id = ?", ('completed', booking_id))
            db.commit()

            db.close()

            return redirect(url_for('payment_success'))  # Redirect to payment success page
        else:
            return render_template('payment_fail.html', error=payment.error)
    else:
        return redirect(url_for('mapcreate'))  # Redirect to map page if there's no paymentId or PayerID

@app.route('/payment/success')
def payment_success():
    # Retrieve booking details along with user's email from the database
    db = sqlite3.connect(app.config['DATABASE'])
    cursor = db.cursor()
    cursor.execute("SELECT booking.*, user.email FROM booking JOIN user ON booking.email = user.email WHERE booking.status='completed'")
    bookings = cursor.fetchall()
    db.close()

    # Pass bookings to the template
    return render_template('payment_success.html', bookings=bookings)



def get_booking_id(email):
    # Fetch booking ID for the payer's email
    db = sqlite3.connect(app.config['DATABASE'])
    cursor = db.cursor()
    cursor.execute("SELECT booking_id FROM booking WHERE email=?", (email,))
    booking_id = cursor.fetchone()[0] if cursor.fetchone() else None
    db.close()
    return booking_id


@app.route('/transactions')
def transactions():
    # Connect to the database
    db = sqlite3.connect(app.config['DATABASE'])
    cursor = db.cursor()
    
    # Fetch transactions from the database
    cursor.execute("SELECT * FROM transaction")
    transactions = cursor.fetchall()

    # Close the database connection
    db.close()

    return render_template('transactions.html', transactions=transactions)


@app.route('/booking_info_day')
def man_day_booking_info():
    # Retrieve booking details along with user's email and payment ID from the database
    db = sqlite3.connect(app.config['DATABASE'])
    cursor = db.cursor()
    cursor.execute(""" SELECT * 
    FROM booking 
    WHERE location_name='Day' AND status='completed'
    """)


    bookings1 = cursor.fetchall()
    db.close()

    # Pass bookings to the correct template
    return render_template('manager dashboard.html', bookings=bookings1)
@app.route('/booking_info_dawn')
def manager_dawn_booking_info():
    # Retrieve booking details along with user's email and payment ID from the database
    db = sqlite3.connect(app.config['DATABASE'])
    cursor = db.cursor()
    cursor.execute(""" 
        SELECT * 
        FROM booking 
        WHERE location_name='Dawn' AND status='completed'
    """)

    bookings = cursor.fetchall()
    db.close()

    # Pass bookings to the template
    return render_template('manager dashboard2.html', bookings=bookings)


# Route to display manager information
@app.route('/manager_info')
def manager_info():
    # Connect to the database
    db = sqlite3.connect(app.config['DATABASE'])
    cursor = db.cursor()

    # Fetch manager information from the database
    cursor.execute("SELECT * FROM managers")
    managers = cursor.fetchall()

    # Close the database connection
    db.close()

    return render_template('admin_dashboard.html', managers=managers)

    
# Define calculate_duration function here or import it from another module
def calculate_duration(time_in, time_out):
    time_in_date = datetime.strptime(time_in, '%H:%M')
    time_out_date = datetime.strptime(time_out, '%H:%M')
    return (time_out_date - time_in_date).total_seconds() / 3600

# Register user
@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm-password']

    # Check if password matches confirm password
    if password != confirm_password:
        return render_template('user register.html', error="Passwords do not match")

    # Connect to the database
    with sqlite3.connect(app.config['DATABASE']) as db:
        cursor = db.cursor()

        # Check if email already exists in the user table
        cursor.execute("SELECT * FROM user WHERE email=?", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            return render_template('user login.html', error="Email already exists. Please use a different email.")

        # Insert user details into the user table
        cursor.execute("INSERT INTO user (email, password, user_type) VALUES (?, ?, 'customer')", (email, password))
        db.commit()

    return redirect('/login')


# Login route for customers
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to the database
        db = sqlite3.connect(app.config['DATABASE'])
        cursor = db.cursor()

        # Check if email and password exist in the user table for a customer
        cursor.execute("SELECT * FROM user WHERE email=? AND password=? AND user_type='customer'", (email, password))
        user = cursor.fetchone()

        if user:
            # Check if the email is already in the session table
            cursor.execute("SELECT * FROM user_session WHERE email=?", (email,))
            existing_session = cursor.fetchone()

            if not existing_session:
                # Insert email into user_session table if it doesn't exist
                cursor.execute("INSERT INTO user_session (email) VALUES (?)", (email,))
                db.commit()  # Commit the changes to the database

            # Close the database cursor
            cursor.close()
            db.close()

            # Initialize the session with the user's email
            session['email'] = email

            # Redirect to user page if email, password, and user type are correct
            return redirect('/map')

        # Close the database cursor and connection if no user found
        cursor.close()
        db.close()

    # For GET requests or failed login attempts, render the login page with an error message
    return render_template('user login.html', error="Invalid email or password")


def get_available_lots(location_name):
    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.cursor()

        # Query to get the number of available lots based on location name
        cursor.execute("SELECT slots_available FROM Location WHERE loc_name = ?", (location_name,))
        row = cursor.fetchone()

        if row:
            return row[0]  # Return the available lots count
        else:
            return "Not available"  # Return a message if location not found or no data available



#admin location change implementation

@app.route('/edit_location', methods=['GET', 'POST'])
def edit_location():
    if request.method == 'POST':
        # Get the form data submitted by the admin
        location_id = request.form['location_id']
        manager_id = request.form['manager_id']
        location_name = request.form['location_name']
        price = request.form['price']

        # Connect to the database
        with sqlite3.connect(app.config['DATABASE']) as db:
            cursor = db.cursor()

            # Update the location details in the location table
            cursor.execute("UPDATE location SET manager_id=?, location_name=?, price=? WHERE id=?", (manager_id, location_name, price, location_id))
            db.commit()

        # Redirect to the dashboard or any other relevant page after editing
        return redirect('/dashboard')  # Adjust the redirect URL as needed

    # For GET requests, render the edit location form or dashboard
    # You can render a form with inputs for location_id, manager_id, location_name, price, etc.
    return render_template('edit_location.html')  # Adjust the template name as needed



# Function to get the user's location using JavaScript
user_location_script = """
<script>
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var userLat = position.coords.latitude;
            var userLng = position.coords.longitude;
            var userLocation = [userLat, userLng];
            console.log("User Location:", userLocation);
            // You can pass the userLocation variable to your Flask route or use it in JavaScript
        });
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
</script>
"""

# Function to calculate the payment amount
def calculate_payment(price_per_hour, time_in, time_out):
    duration_hours = (time_out - time_in).seconds / 3600
    total_price = price_per_hour * duration_hours
    return total_price


@app.route('/map')
def mapcreate():
    # Connect to the database
    db = sqlite3.connect(app.config['DATABASE'])
    cursor = db.cursor()
    
    # Fetch locations from the database
    cursor.execute("SELECT * FROM Location")
    locations = cursor.fetchall()

    # Calculate the mean latitude and longitude
    mean_latitude = sum(loc[1] for loc in locations) / len(locations)  # Assuming latitude is at index 1
    mean_longitude = sum(loc[2] for loc in locations) / len(locations)  # Assuming longitude is at index 2
    
    # Render the map template
    return render_template('userpage.html', locations=locations, mean_latitude=mean_latitude, mean_longitude=mean_longitude)

if __name__ == '__main__':
    app.run(debug=True)