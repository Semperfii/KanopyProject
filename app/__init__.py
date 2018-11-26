from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='../app/templates')
app.config.from_object('settings')
db = SQLAlchemy(app)

from app import views