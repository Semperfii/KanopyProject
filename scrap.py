import requests 
import pandas as pd

from datetime import datetime

repo = 'torvalds/linux'



def retrieveData(per_page=100, n_page=1):
    df_commits = pd.DataFrame(columns=['author.date', 'author.email', 'author.name', 'comment_count',
       'committer.date', 'committer.email', 'committer.name', 'message',
       'tree.sha', 'tree.url', 'url', 'verification.payload',
       'verification.reason', 'verification.signature',
       'verification.verified'])
    for page in range(n_page):
        r = requests.get('https://api.github.com/repos/{0}/commits?per_page={1}&page={2}'.format(repo, per_page, page)).json()
        #commits = [r[i]['commit'] for i in range(per_page)]
        keys = ['node_id', 'commit', 'author']
        data = [{x:r[i][x] for x in keys} for i in range(per_page)]

        df = pd.io.json.json_normalize(data)
        print(df.columns)
        df = df[['node_id','commit.url', 'author.name', 'author.email', 'author.date']].rename(columns=
        {
            'node_id': 'id',
            'commit.url': 'url',
            'author.name': 'author_name',
            'author.email': 'author_email',
            'author.date': 'date'
        })
        print(df.columns)
        #commits = [r[i]['commit'] + r[i]['node_id'] for i in range(per_page)]
        # authors = [r[i]['author'] for i in range(per_page)]

        # df_temp_commits = pd.io.json.json_normalize(commits)
        # df_temp_authors = pd.io.json.json_normalize(authors)
        # print(df_temp_authors)


        #df = pd.DataFrame.from_dict(commits, orient='columns')
        # df_commits = pd.concat([df_commits, df_temp_commits], ignore_index=True)

def retrieveStats():
    r = requests.get('https://api.github.com/repos/{0}/stats/commit_activity'.format(repo)).json()
    days = []
    commits = []
    for weeks in r:
        week = weeks['week']
        for i in range(7):
            day = week + i*86400
            days.append(datetime.utcfromtimestamp(day).strftime('%Y-%m-%d %H:%M:%S'))
            commits.append(weeks['days'][i])
    commits_per_day = {
        'day': days,
        'number_commits': commits
    }
    df = pd.DataFrame.from_dict(commits_per_day)
    print(df)


    print(r)

retrieveStats()



#commit = [commits[i]['commit']['author'] for i in range(n_commits)]

# comments_url = commits['comments_url']
# commit = commits['commit']
# committer = commits['committer']
# html_url = commits['html_url']
# node_id = commits['node_id']
# parents = commits['parents']
# sha = commits['sha']
# url = commits['url']




#print(df)
# print(len(commits))