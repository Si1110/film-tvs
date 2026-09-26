import sys, json, re, os, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
import requests

BDUSS = os.environ.get('BDUSS', '')
STOKEN = os.environ.get('STOKEN', '')

s = requests.Session()
s.cookies.set('BDUSS', BDUSS)
s.cookies.set('STOKEN', STOKEN)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://pan.baidu.com/',
}

# Get bdstoken
r = s.get('https://pan.baidu.com/', headers=headers, timeout=15)
m = re.search(r'bdstoken[":=\s]+([a-f0-9]+)', r.text[:5000])
bdstoken = m.group(1) if m else ''
print(f'bdstoken: {bdstoken}')

# Test with a real Baidu share
surl = '1gKy-i190Ui4GUR8p1A-zMQ'
pwd = '01g5'

# Step 1: Share init
init_url = 'https://pan.baidu.com/share/init?surl=' + surl
r = s.post(init_url, data={'pwd': pwd, 'vcode': '', 'vcode_str': ''}, headers={
    **headers,
    'Content-Type': 'application/x-www-form-urlencoded',
}, timeout=15)
print(f'Init status: {r.status_code}')
raw = r.content
print(f'Raw response: {raw[:500]}')
try:
    d = r.json()
    print(json.dumps(d, ensure_ascii=False, indent=2)[:1000])
except:
    print('Response is not JSON, trying to parse HTML')
    html = r.text
    m2 = re.search(r'window\.yunData\s*=\s*({.*?});', html)
    if m2:
        d = json.loads(m2.group(1))
        print(json.dumps(d, ensure_ascii=False, indent=2)[:1000])
    else:
        print(html[:500])
