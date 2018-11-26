# Kanopy Project

Data Analysis of the commits of the Linux Github Repository.

## Installing

To install the project, run in the directory :

```
docker-compose up --build
```

To initialize the database (once the docker is built) run :

```
docker exec -it app_web_1 python dbinit.py
```

The website is available at ```localhost:5000```.

## The project

### Performing the actions

All the csv reports :
* All the commits made between two given dates
* Number of commits made by each author
* Number of average commits each week day of the current month
* Cumulative commits made daily during the current month

can be downloaded from the web app. The button ```Get Data``` is used to get the data from the API. If new commits have been made, pressing again this button will update the database.

### My approach

I used only Python - with a few HTML -  to make this project.

First of all, I focused on retrieving the data from the Github API, and processing it to be able to store it in a database. I chose to get the essential data from each commit (sha, url, comment count, date, author name & email, committer name & email). However I realized that the rate limit of 60 API requests per hour limited the maximum amount of commits retrieved to 6000 (maximum 100 per page). Some months from last year exceeded these 6000 commits. That is why, in order to have  relevant monthly insights, I chose to only get the last 2000 commits and also get the data from ```https://api.github.com/repos/torvalds/linux/stats/commit_activity``` : number of daily commits during the previous year. The only - minor - drawback is that is does not include the merge commits.


Then I created a server using Flask in order to have a user-friendly interface for the project. I chose to use a MySQL database to store the data from the commits, because it is a reliable and very popular option, although it is very similar to PostgreSQL. Then I dockerized both the web app and the database and created a script initializing the database from the models stored in ```models.py```. 

There are two models, one for the table commit and , storing the data from the request to ```https://api.github.com/repos/torvalds/linux/commits```, and one for the table "daily", storing the data from the request to ```https://api.github.com/repos/torvalds/linux/stats/commit_activity```. These models are created thanks to SQLAlchemy ORM. 

Another issue was creating csv reports and downloading them, using the data from the SQL queries. I used StringIO to write in the file (no file is stored on the server). Every csv report can be downloaded from the web app.

Finally I created charts using ChartJS to display some charts on the web views (corresponding to the data from the csv reports).

### Libraries 

* Data gathering and processing : Requests and Pandas

* Data storage : Flask-Sqlalchemy and PyMysql

* Server : Flask

* Charts : ChartJS

### Time spent

I spent around 10 hours on this project :
* Gathering data from the Github API : 2h
* Creating the server and dockerizing the project : 3h
* Database integration : 2h
* Improvements of the web app : 2h
* Charts : 1h

## Improvements

### Other reports

The next thing I would have done if I had the time would be to add other parameters for the reports, and to display the corresponding charts. These could be :
* Average number of commits each time slot of the day ( 12am - 5am, 5am - 10am, 10am - 12pm, 12pm - 2pm, 2pm - 5pm, 5pm - 8pm, 8pm - 12am)
* Authors with most commits in the current month compared to the previous month

### Using the message data

At first I had a hard time including the message data in the database because of a wrong utf8 encoding. I finally could get the messages, however I chose not to put them in the report for greater clearity. But this data could be very valuable, and another analysis could be performed directly on it !

### Github authentication


More commits could be retrieved from the Github API with a valid oauth tocken (the rate limit would be 5000 requests per hour).
















