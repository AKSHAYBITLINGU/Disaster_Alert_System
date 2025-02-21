import sqlite3
import logging

def init_db():
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Users table
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                location TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL
            )"""
        )

        # Sent alerts table
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS sent_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )"""
        )

        conn.commit()
        conn.close()
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")