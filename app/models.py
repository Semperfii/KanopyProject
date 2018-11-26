from app import db

class Commit(db.Model):
    sha = db.Column(db.String(100), primary_key=True)
    url = db.Column(db.String(100))
    message = db.Column(db.Text)
    comment_count = db.Column(db.Integer)
    author_name = db.Column(db.String(100))
    author_email = db.Column(db.String(100))
    committer_name = db.Column(db.String(100))
    committer_email = db.Column(db.String(100))
    date = db.Column(db.String(50))

    def __repr__(self):
        return '<Commit %r>' % self.id

class Daily(db.Model):
    date = db.Column(db.DateTime, primary_key=True)
    day = db.Column(db.String(10))
    day_index = db.Column(db.Integer)
    number_commits = db.Column(db.Integer)

    def __repr__(self):
        return '<Daily %r>' % self.day






