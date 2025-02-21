import os
from flask_mail import Mail
from flask import Flask
from dotenv import load_dotenv
load_dotenv()

mail = Mail()

def configure_mail(app: Flask):
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587  # Typically 587 for TLS
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_USERNAME")

    mail.init_app(app)  # Initialize Flask-Mail with the app
