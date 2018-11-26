import requests 

repo = 'torvalds/linux'

r = requests.get('https://api.github.com/repos/{0}/commits'.format(repo))

commits = r.json()[0]['commit']

print(commits)