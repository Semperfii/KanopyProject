from app import db

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)

    def __init__(self, count):
        self.count = count

    def __repr__(self):
        return '<Count %r>' % self.count

class Commit(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    #message = db.Column(db.Text)
    url = db.Column(db.String(100))
    author_name = db.Column(db.String(40))
    author_email = db.Column(db.String(40))
    date = db.Column(db.String(50))

    def __repr__(self):
        return '<Commit %r>' % self.id

class Daily(db.Model):
    date = db.Column(db.DateTime, primary_key=True)
    day = db.Column(db.String(10))
    number_commits = db.Column(db.Integer)

    def __repr__(self):
        return '<Daily %r>' % self.day






