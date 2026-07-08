import sys, json, re, os, urllib.parse, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

BDUSS = os.environ.get('BDUSS', '')
STOKEN = os.environ.get('STOKEN', '')

cookie_str = f"BDUSS={BDUSS}; STOKEN={STOKEN}"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://pan.baidu.com/',
    'Cookie': cookie_str,
}

def fetch(url, data=None):
    if data:
        data_bytes = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, headers=headers)
    else:
        req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        raw = resp.read()
        text = raw.decode('utf-8', errors='replace')
        return text, resp.status, resp.headers
    except urllib.request.HTTPError as e:
        raw = e.read()
        text = raw.decode('utf-8', errors='replace')
        return text, e.code, e.headers

# Test: Get the actual share page first to see what's there
surl = '1gKy-i190Ui4GUR8p1A-zMQ'
pwd = '01g5'

share_url = f'https://pan.baidu.com/s/1{surl}'
html, status, _ = fetch(share_url)
print(f'Share page status: {status}')
print(f'Length: {len(html)}')

# Look for yunData, shareid, uk in page
patterns = [
    (r'window\.yunData\s*=\s*({.*?});', 'yunData'),
    (r'"shareid"\s*:\s*"?(\d+)"?', 'shareid'),
    (r'"uk"\s*:\s*"?(\d+)"?', 'uk'),
    (r'"bdstoken"\s*:\s*"([^"]+)"', 'bdstoken'),
    (r'"sekey"\s*:\s*"([^"]+)"', 'sekey'),
    (r'"randsk"\s*:\s*"([^"]+)"', 'randsk'),
]
found = {}
for pat, name in patterns:
    m = re.search(pat, html)
    if m:
        val = m.group(1)[:100]
        found[name] = val
        print(f'{name}: {val}')
    else:
        print(f'{name}: NOT FOUND')

# Try to extract from file_list or file_data
for pat_name in ['file_list', 'file_data', 'data', 'list']:
    m = re.search(r'"' + pat_name + r'"\s*:\s*(\[[\s\S]*?\])\s*[,;}]', html)
    if m:
        try:
            data = json.loads(m.group(1))
            print(f'\n{pat_name} found: {json.dumps(data[:3], ensure_ascii=False, indent=2)[:500]}')
        except:
            print(f'{pat_name} found but not parseable')
        break
else:
    print('\nNo file list found in page')
