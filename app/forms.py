from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from wtforms.fields.html5 import DateField

class ReportForm(FlaskForm):
    begin_date = DateField('Begin Date', format='%Y-%m-%d')
    end_date = DateField('End Date', format='%Y-%m-%d')
    authors_commits = BooleanField('Authors Commits')
    average_commits = BooleanField('Average Commits')
    daily_commits = BooleanField('Daily Commits')
    submit = SubmitField('Download')

class DataForm(FlaskForm):
    get_data = SubmitField('Get Data')
