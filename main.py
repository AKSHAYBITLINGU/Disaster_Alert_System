from flask import Flask, render_template, request, redirect, flash
from database import init_db
from mail_config import configure_mail
from navigation import navigation
import os

init_db()

# Initialize Flask app
app = Flask(__name__)
configure_mail(app)
app.register_blueprint(navigation)
app.secret_key = os.getenv("SECRET_KEY")

# Initialize database and run the app
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
