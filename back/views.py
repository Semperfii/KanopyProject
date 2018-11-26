import os
import pandas as pd
import requests
import csv
from io import StringIO
from datetime import datetime

from flask import render_template, send_from_directory, current_app, request, flash, redirect, make_response

from app import app, db
from back.models import *
from back.forms import ReportForm

def get_csv(sql_query, header, file_name):
    data = db.engine.execute(sql_query)
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(header)
    cw.writerows(data)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename={}.csv".format(file_name)
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/', methods = ['POST', 'GET'])
def contact():
    if request.method == 'POST':
        if request.form['action'] == 'Get data':
            repo = 'torvalds/linux'
            # Add the data from commits
            per_page = 100
            page = 1
            r = requests.get('https://api.github.com/repos/{0}/commits?per_page={1}&page={2}'.format(repo, per_page, page)).json()
            keys = ['node_id', 'commit']
            data = [{x:r[i][x] for x in keys} for i in range(per_page)]
            df = pd.io.json.json_normalize(data)
            df = df[['node_id','commit.url', 'commit.author.name', 'commit.author.email', 'commit.author.date']].rename(columns=
            {
                'node_id': 'id',
                'commit.url': 'url',
                'commit.author.name': 'author_name',
                'commit.author.email': 'author_email',
                'commit.author.date': 'date'
            })
            df.to_sql(name='tempTable', con=db.engine, index=False, if_exists='replace')
            sql = """INSERT INTO commit (id, url, author_name, author_email, date)
            SELECT t.id, t.url, t.author_name, t.author_email, t.date
            FROM tempTable t
            WHERE NOT EXISTS 
                (SELECT 1 FROM commit f
                    WHERE t.id = f.id)"""
            db.engine.execute(sql)
            # Add the daily commits data
            r2 = requests.get('https://api.github.com/repos/{0}/stats/commit_activity'.format(repo)).json()
            week_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            days = []
            dates = []
            commits = []
            for weeks in r2:
                week = weeks['week']
                for i in range(7):
                    date = week + i*86400
                    dates.append(datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S'))
                    commits.append(weeks['days'][i])
                    days.append(week_days[i])
            commits_per_day = {
                'dates': dates,
                'days': days,
                'number_commits': commits
            }
            df = pd.DataFrame.from_dict(commits_per_day)
            df.to_sql(name='daily', con=db.engine, index=False, if_exists='replace')
            return render_template('home.html')
    elif request.method == 'GET':
        return render_template('home.html')

@app.route('/reports/authors_commits', methods = ['POST', 'GET'])
def authors():
    form = ReportForm()
    if request.method == 'POST':
        sql_query = """SELECT author_name, COUNT(id) as Number_Commits  FROM commit GROUP BY author_name ORDER BY Number_Commits DESC"""
        header = ['Author','Number of Commits']
        file_name='authors_report'
        return get_csv(sql_query, header, file_name)
    elif request.method == 'GET':
        return render_template('authors_commits.html', form=form)

@app.route('/reports/dates_commits', methods = ['POST', 'GET'])
def dates(file_name='dates_report'):
    form = ReportForm()
    if request.method == 'POST':
        sql_query = """SELECT * FROM commit WHERE date >= '{}' AND date <= '{}' """.format(form.begin_date.data, form.end_date.data)
        header = ['Author','Number of Commits']
        file_name='date_report'
        return get_csv(sql_query, header, file_name)
    elif request.method == 'GET':
        return render_template('dates_commits.html', form=form)



@app.route('/reports')
def reports():
    repo = 'torvalds/linux'
    per_page = 100
    page = 1
    r = requests.get('https://api.github.com/repos/{0}/commits?per_page={1}&page={2}'.format(repo, per_page, page)).json()
    #commits = [r[i]['commit'] for i in range(per_page)]
    keys = ['node_id', 'commit']
    data = [{x:r[i][x] for x in keys} for i in range(per_page)]

    df = pd.io.json.json_normalize(data)
    df = df[['node_id','commit.url', 'commit.author.name', 'commit.author.email', 'commit.author.date']].rename(columns=
    {
        'node_id': 'id',
        'commit.url': 'url',
        'commit.author.name': 'author_name',
        'commit.author.email': 'author_email',
        'commit.author.date': 'date'
    })
    df.to_sql(name='commit', con=db.engine, index=False, if_exists='replace')
    return("")
    # Use for update

    #  sql = """INSERT INTO commit (id, url)
    #      SELECT t.id, t.message, t.url
    #      FROM tempTable t
    #      WHERE NOT EXISTS 
    #          (SELECT 1 FROM counter f
    #              WHERE t.id = f.id)"""
    # db.engine.execute(sql)


@app.route('/df')
def dataf():
    data = { 'test': [34,645], 'test2': [12, 34] }
    df = pd.DataFrame.from_dict(data, orient='index', columns=['id', 'count'])
    df.to_sql(name='tempTable', con=db.engine, index=False, if_exists='replace')
    sql = """INSERT INTO counter (id, count)
        SELECT t.id, t.count
        FROM tempTable t
        WHERE NOT EXISTS 
            (SELECT 1 FROM counter f
                WHERE t.id = f.id
                AND t.count = f.count)"""
    db.engine.execute(sql)
    return "<h1>Counter test:</h1>" #+ str(counter)

