# Create tables for all models
from app import db
from back.models import *
db.drop_all()
db.create_all()
