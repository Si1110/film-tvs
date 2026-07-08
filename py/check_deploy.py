import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')
url = 'https://api.github.com/repos/Si1110/film-tvs/actions/runs?per_page=3'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = json.loads(urllib.request.urlopen(req).read())
for run in data['workflow_runs']:
    sha = run['head_sha'][:8]
    print(f'{run["id"]} | {run["status"]} | {run["conclusion"]} | {sha} | {run["created_at"]}')
