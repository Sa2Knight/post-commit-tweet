import requests
import json

EVENTS_URL     = "https://api.github.com/users/sa2knight/events"
REPOSITORY_URL = "https://api.github.com/repos"

def get_repository_description(repo_name):
  url = f"{REPOSITORY_URL}/{repo_name}"
  response = requests.get(url)
  repository = json.loads(response.text)
  return repository['description']

def get_recent_push_event():
  response = requests.get(EVENTS_URL)
  events   = json.loads(response.text)
  recent_event = list(filter(lambda e: e['type'] == 'PushEvent', events))[0]
  repo_name    = recent_event['repo']['name']
  commits      = list(map(lambda c: parse_commit_log(repo_name, c), recent_event['payload']['commits']))
  return {
    'id':         recent_event['id'],
    'repository': get_repository_description(recent_event['repo']['name']),
    'commits':    commits,
  }

def parse_commit_log(repo_name, commit):
  return {
    'url': f"https://github.com/{repo_name}/commit/{commit['sha']}",
    'message': commit['message']
  }

event = get_recent_push_event()
tweet = f"""
@tos
Githubにコミットをプッシュしました。
[{event['repository']}] 「{event['commits'][0]['message']}」
""".strip()
if 1 < len(event['commits']):
  tweet += f"ほか{len(event['commits']) - 1}件"
tweet += f"\n{event['commits'][0]['url']}"

print(tweet)
