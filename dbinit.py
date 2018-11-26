# Create tables for all models
from app import db
from app.models import *

db.drop_all()
db.create_all()
