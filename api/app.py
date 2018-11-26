import os

from flask import Flask
from flask import render_template
from flask import request

import pymysql
import json

from models import db, Commit

app = Flask(__name__)

MYSQL = {
    'user': 'usr',
    'pw': 'pwd',
    'db': 'test',
    'host': 'localhost',
    'port': '5432',
}

mysql_file = 'mysql+pymysql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % MYSQL

mysql_file_test = 'mysql+pymysql://root:password@db:3306/commits'

# project_dir = os.path.dirname(os.path.abspath(__file__))
# database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdatabase.db"))

app.config['SQLALCHEMY_DATABASE_URI'] = mysql_file_test
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

db.init_app(app)




@app.route('/', methods=["GET", "POST"])
def main():
    if request.form:
        commit = Commit(title=request.form.get("title"))
        db.session.add(commit)
        db.session.commit()
    return render_template("home.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)