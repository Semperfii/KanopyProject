import os
import pandas as pd
import requests
import csv
from io import StringIO
from datetime import datetime
import time
import sys

from flask import render_template, Markup, current_app, request, redirect, make_response

from app import app, db
from app.models import *
from app.forms import ReportForm, DataForm

duration_day_ms = 86400
this_month = datetime.utcfromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')
last_month = datetime.utcfromtimestamp(int(time.time()) - 31*duration_day_ms).strftime('%Y-%m-%d %H:%M:%S')

def getCsv(data, header, file_name):
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(header)
    cw.writerows(data)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename={}.csv".format(file_name)
    output.headers["Content-type"] = "text/csv"
    return output

def getData():
    repo = 'torvalds/linux'
    # Add the data from commits
    per_page = 100
    page = 1
    r = requests.get('https://api.github.com/repos/{0}/commits?per_page={1}&page={2}'.format(repo, per_page, page)).json()
    
    keys = ['sha', 'commit']
    data = [{x:r[i][x] for x in keys} for i in range(per_page)]
    df = pd.io.json.json_normalize(data)
    df = df[['sha', 'commit.url', 'commit.comment_count', 'commit.author.name', 'commit.author.email', 'commit.author.date', 'commit.committer.name', 'commit.committer.email']].rename(columns=
    {
        'commit.url': 'url',
        'commit.comment_count': 'comment_count',
        'commit.author.name': 'author_name',
        'commit.author.email': 'author_email',
        'commit.author.date': 'date',
        'commit.committer.name': 'committer_name',
        'commit.committer.email': 'committer_email'
    })
    # We use a temporary table to be able to update the data in the commit table
    df.to_sql(name='tempTable', con=db.engine, index=False, if_exists='replace')
    sql = """INSERT INTO commit (sha, url, comment_count, author_name, author_email, committer_name, committer_email, date)
    SELECT t.sha, t.url, t.comment_count, t.author_name, t.author_email, t.committer_name, t.committer_email, t.date
    FROM tempTable t
    WHERE NOT EXISTS 
        (SELECT 1 FROM commit f
            WHERE t.sha = f.sha)"""
    db.engine.execute(sql)
    # Add the daily commits data
    r2 = requests.get('https://api.github.com/repos/{0}/stats/commit_activity'.format(repo)).json()
    week_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    week_days_index = [6,0,1,2,3,4,5]
    days = []
    days_index = []
    dates = []
    commits = []
    for weeks in r2:
        week = weeks['week']
        for i in range(7):
            date = week + i*duration_day_ms
            dates.append(datetime.utcfromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S'))
            commits.append(weeks['days'][i])
            days.append(week_days[i])
            days_index.append(week_days_index[i])
    commits_per_day = {
        'date': dates,
        'day': days,
        'day_index': days_index,
        'number_commits': commits
    }
    df = pd.DataFrame.from_dict(commits_per_day)
    df.to_sql(name='daily', con=db.engine, index=False, if_exists='replace')

@app.route('/', methods = ['POST', 'GET'])
def home():
    dataForm = DataForm()
    if dataForm.get_data.data:
        getData()
        return render_template('home.html', dataForm=dataForm)
    elif request.method == 'GET':
        return render_template('home.html', dataForm=dataForm)

@app.route('/reports/authors_commits', methods = ['POST', 'GET'])
def authors():
    reportForm = ReportForm()
    dataForm = DataForm()
    sql_query_chart = """SELECT author_name, COUNT(sha) as Number_Commits  FROM commit GROUP BY author_name ORDER BY Number_Commits DESC"""
    data_chart = db.engine.execute(sql_query_chart)
    hex_colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
    hex_index = 0
    labels = []
    values = []
    colors = []
    rows = data_chart.fetchall()
    for row in rows:
        labels.append(row[0])
        values.append(float(row[1]))
        colors.append(hex_colors[hex_index%len(hex_colors)])
        hex_index += 1
    if reportForm.submit.data:
        sql_query = """SELECT author_name, author_email, COUNT(sha) as Number_Commits  FROM commit GROUP BY author_name, author_email ORDER BY Number_Commits DESC"""
        data = db.engine.execute(sql_query)
        header = ['Author Name', 'Author Email', 'Number of Commits']
        file_name='authors_report'
        return getCsv(data, header, file_name)
    elif dataForm.get_data.data:
        getData()
        return render_template('authors_commits.html', form=reportForm, dataForm=dataForm, set=zip(values, labels, colors))
    elif request.method == 'GET':
        return render_template('authors_commits.html', form=reportForm, dataForm=dataForm, set=zip(values, labels, colors))

@app.route('/reports/dates_commits', methods = ['POST', 'GET'])
def dates():
    reportForm = ReportForm()
    dataForm = DataForm()
    if reportForm.submit.data:
        sql_query = """SELECT * FROM commit WHERE date >= '{0}' AND date <= '{1}' """.format(reportForm.begin_date.data, reportForm.end_date.data)
        data = db.engine.execute(sql_query)
        header = ['Sha', 'Url', 'Comment Count', 'Author Name', 'Author Email', 'Committer Name', 'Committer Email', 'Date']
        file_name='date_report'
        return getCsv(data, header, file_name)
    elif dataForm.get_data.data:
        getData()
        return render_template('dates_commits.html', form=reportForm, dataForm=dataForm)
    elif request.method == 'GET':
        return render_template('dates_commits.html', form=reportForm, dataForm=dataForm)

@app.route('/reports/week_days_commits', methods = ['POST', 'GET'])
def week_days():
    reportForm = ReportForm()
    dataForm = DataForm()
    sql_query_chart = """SELECT day, day_index, SUM(number_commits) AS commits FROM daily WHERE date <= '{0}' AND date >= '{1}' GROUP BY day, day_index ORDER BY day_index ASC;""".format(this_month, last_month)
    data_chart = db.engine.execute(sql_query_chart)
    labels = []
    values = []
    rows = data_chart.fetchall()
    for row in rows:
        labels.append(row[0])
        values.append(float(row[2]))
    print(labels, values, file=sys.stderr)
    if reportForm.submit.data:
        sql_query = """SELECT day, SUM(number_commits) AS commits FROM daily WHERE date <= '{0}' AND date >= '{1}' GROUP BY day ORDER BY commits DESC;""".format(this_month, last_month)
        data = db.engine.execute(sql_query)
        header = ['Week Day','Number of Commits']
        file_name='week_days_report'
        return getCsv(data, header, file_name)
    elif dataForm.get_data.data:
        getData()
        return render_template('week_days_commits.html', form=reportForm, dataForm=dataForm, max=300, labels=labels, values=values)
    elif request.method == 'GET':
        return render_template('week_days_commits.html', form=reportForm, dataForm=dataForm, max=300, labels=labels, values=values)

@app.route('/reports/daily_commits', methods = ['POST', 'GET'])
def daily():
    reportForm = ReportForm()
    dataForm = DataForm()
    sql_query_chart = """SELECT date, number_commits FROM daily WHERE date <= '{0}' AND date >= '{1}';""".format(this_month, last_month)
    data_chart = db.engine.execute(sql_query_chart)
    labels = []
    values = []
    rows = data_chart.fetchall()
    for row in rows:
        labels.append(row[0])
        values.append(float(row[1]))
    if reportForm.submit.data:
        sql_query = """SELECT date, number_commits FROM daily WHERE date <= '{0}' AND date >= '{1}';""".format(this_month, last_month)
        data = db.engine.execute(sql_query)
        header = ['Date','Number of Commits']
        file_name='daily_report'
        return getCsv(data, header, file_name)
    elif dataForm.get_data.data:
        getData()
        return render_template('daily_commits.html', form=reportForm, dataForm=dataForm, max=180, labels=labels, values=values)
    elif request.method == 'GET':
        return render_template('daily_commits.html', form=reportForm, dataForm=dataForm, max=180, labels=labels, values=values)

