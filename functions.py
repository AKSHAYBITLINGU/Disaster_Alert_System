import logging
import sqlite3
from datetime import datetime
import sys
from mail_config import mail
from flask_mail import Message

# Configure logging
# Remove existing handlers (if any)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure logging to log both to file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("disaster_alert.log"),
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)

logging.info("Logging initialized successfully!")

def fetch_users():
    # Connect to the SQLite database
    conn = sqlite3.connect('users.db')  # Replace with your database file
    cursor = conn.cursor()

    # Fetch all users from the 'users' table
    cursor.execute("SELECT username, location, email FROM users WHERE role='user'")
    users = cursor.fetchall()

    # Close the database connection
    conn.close()

    return users

def fetch_admins():
    # Connect to the SQLite database
    conn = sqlite3.connect('users.db')  # Replace with your database file
    cursor = conn.cursor()

    # Fetch all users from the 'users' table
    cursor.execute("SELECT username, location, email FROM users WHERE role='admin'")
    admins = cursor.fetchall()

    # Close the database connection
    conn.close()

    return admins

def get_users_by_location(location):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE location = ?", (location,))
    users = cursor.fetchall()
    conn.close()
    return [user[0] for user in users]


def send_alert(location, message):
    users = get_users_by_location(location)
    if not users:
        logging.warning(f"No users found in location: {location}")
        return False

    # logging.info(f"Sendingstar alert to {len(users)} users in {location}: {message}")
    print(f"Sending alert to {len(users)} users in {location}: {message}")  # Print output to console
    logging.info(f"Sending alert to {len(users)} users in {location}: {message}")  # Log output


    # Store the alert in the database
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO sent_alerts (location, message, timestamp) VALUES (?, ?, ?)",
                       (location, message, timestamp))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error storing sent alert in the database: {e}")

    # Send email notifications to users
    for email in users:
        try:
            with mail.connect() as conn:
                msg = Message("🚨 Disaster Alert 🚨", recipients=[email])
                msg.body = f"⚠️ ALERT for {location} ⚠️\n{message}\nStay safe and follow safety guidelines."
                conn.send(msg)
                logging.info(f"Email sent to {email}: {message}")
        except Exception as e:
            logging.error(f"Error sending email to {email}: {e}")

    return True

def fetch_disaster_alerts():
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT location, message, timestamp FROM sent_alerts ORDER BY timestamp DESC")
        alerts = cursor.fetchall()
        conn.close()
        return alerts
    except Exception as e:
        logging.error(f"Error fetching disaster alerts: {e}")
        return []
