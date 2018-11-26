from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Commit(db.Model):
    title = db.Column(db.String(60), unique=True, nullable=False, primary_key=True)

    def __repr__(self):
        return "<Title: {}>".format(self.title)
