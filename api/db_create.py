from app import app
from models import db, Commit

with app.app_context():
    db.init_app(app)
    db.create_all()
    db.session.commit()