import twitter
import requests
import json
import os

FILE_NAME      = "last_id"
EVENTS_URL     = "https://api.github.com/users/sa2knight/events"
REPOSITORY_URL = "https://api.github.com/repos"

def tweet(text):
  auth = twitter.OAuth(consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
                       consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
                       token=os.environ['TWITTER_ACCESS_TOKEN'],
                       token_secret=os.environ['TWITTER_ACCESS_SECRET'])
  t = twitter.Twitter(auth=auth)
  t.statuses.update(status=text)

def tweet_event(event):
  tweet_text = f"""
  @null

  Githubにコミットをプッシュしました。

  [{event['repository']}]

  「{event['commits'][0]['message']}」
  """.strip()
  if 1 < len(event['commits']):
    tweet_text += f"ほか{len(event['commits']) - 1}件"
  tweet_text += f"\n\n{event['commits'][0]['url']}"
  tweet(tweet_text)

def save_id(id):
  with open(FILE_NAME, 'w') as f:
    f.write(id)

def load_id():
  if os.path.exists(FILE_NAME):
    with open(FILE_NAME, 'r') as f:
      return f.readline()
  else:
    return ''

def is_new_id(id):
  return id != load_id()

def parse_commit_log(repo_name, commit):
  return {
    'url': f"https://github.com/{repo_name}/commit/{commit['sha']}",
    'message': commit['message']
  }

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

event = get_recent_push_event()
if is_new_id(event['id']):
  tweet_event(event)
  save_id(event['id'])
  print('ツイートを投稿しました')
else:
  print('ツイートは不要です')

