from flask import Blueprint, render_template, request, redirect, flash, session
from functions import send_alert, fetch_disaster_alerts, fetch_users, fetch_admins
import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

navigation = Blueprint('navigation', __name__)

@navigation.route("/")
def home():
    if 'username' in session:
        username = session['username']
        role = session['role']

        # Redirect normal users to the dashboard
        if role == "user":
            return redirect('/dashboard')

        # Admin users will see the home page stats
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Fetch the number of users
        cursor.execute("SELECT seq FROM sqlite_sequence WHERE name=?", ("users",))
        result_users = cursor.fetchone()
        num_users = result_users[0] if result_users else 0

        # Fetch the number of alerts
        cursor.execute("SELECT seq FROM sqlite_sequence WHERE name=?", ("sent_alerts",))
        result_alerts = cursor.fetchone()
        num_alerts = result_alerts[0] if result_alerts else 0

        conn.close()

        return render_template('index.html', username=username, role=role, num_users=num_users, num_alerts=num_alerts)
    
    # Redirect to login if the user is not authenticated
    return redirect('/login')

@navigation.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        location = request.form["location"]
        email = request.form["email"]

        # Default role for new users
        role = "user"

        # Store user data in the database
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, location, email, role) VALUES (?, ?, ?, ?, ?)",
                       (username, password, location, email, role))
        conn.commit()
        conn.close()

        # Start a new session for the registered user
        session['username'] = username
        session['role'] = role  # Assign role as "user"

        return redirect("/dashboard")  # Redirect user to dashboard after registration

    return render_template("register.html")


@navigation.route("/send_alert", methods=["GET", "POST"])
def send_alert_route():
    if request.method == "POST":
        location = request.form["location"]
        message = request.form["message"]

        if send_alert(location, message):
            flash(f"Alert sent to users in {location}.", "success")
        else:
            flash(f"No users found in {location}.", "error")
        return redirect("/")
    return render_template("send_alert.html")

@navigation.route("/alerts")
def view_alerts():
    alerts = fetch_disaster_alerts()
    return render_template("alerts.html", alerts=alerts)

@navigation.route("/users")
def view_users():
    users = fetch_users()
    return render_template("users.html", users=users)

@navigation.route("/admins")
def view_admins():
    admins = fetch_admins()
    print(admins)
    return render_template("admins.html", admins=admins)

@navigation.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database to verify credentials
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            session['role'] = user[0]  # Store the user's role (admin or user)

            if user[0] == 'admin':  
                return redirect('/')  # Redirect admin to home
            else:
                return redirect('/dashboard')  # Redirect regular user to dashboard
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')

@navigation.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')  # Redirect to login if not logged in

    username = session['username']
    role = session['role']

    # Fetch user details from the database
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT email, location FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        email, location = user
        return render_template('dashboard.html', username=username, email=email, location=location, role=role)
    else:
        return "User not found. Please log in again."
    
@navigation.route("/update_location", methods=["POST"])
def update_location():
    if "username" not in session:
        return redirect("/login")  # Redirect to login if not logged in

    new_location = request.form["new_location"]
    username = session["username"]

    # Update the location in the database
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET location=? WHERE username=?", (new_location, username))
    conn.commit()
    conn.close()

    return redirect("/dashboard")  # Reload the dashboard with updated details


@navigation.route('/logout')
def logout():
    # Clear the session
    session.pop('username', None)
    session.pop('role', None)
    return redirect('/login')
