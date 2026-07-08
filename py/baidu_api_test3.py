import sys, json, re, os, zlib, io
sys.stdout.reconfigure(encoding='utf-8')
import requests
import urllib.request
import http.cookiejar

BDUSS = os.environ.get('BDUSS', '')
STOKEN = os.environ.get('STOKEN', '')

# Use urllib directly to avoid requests' gzip issues
def make_request(url, data=None, method='GET'):
    parsed = urllib.parse.urlparse(url)
    # Build cookie header
    cookie_str = f"BDUSS={BDUSS}; STOKEN={STOKEN}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://pan.baidu.com/',
        'Cookie': cookie_str,
    }
    
    if data and method == 'POST':
        data_bytes = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method='POST')
    else:
        req = urllib.request.Request(url, headers=headers, method=method)
    
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        raw = resp.read()
        # Try to detect encoding and decode
        try:
            text = raw.decode('utf-8')
        except:
            try:
                text = raw.decode('gbk')
            except:
                text = raw.decode('utf-8', errors='replace')
        return text, resp.status
    except urllib.request.HTTPError as e:
        raw = e.read()
        try:
            text = raw.decode('utf-8')
        except:
            text = raw.decode('gbk', errors='replace')
        return text, e.code

# Step 1: Get bdstoken from home page
html, status = make_request('https://pan.baidu.com/')
m = re.search(r'bdstoken[":=\s]+([a-f0-9]+)', html[:10000])
bdstoken = m.group(1) if m else ''
print(f'bdstoken: {bdstoken}')

# Step 2: Test share init
surl = '1gKy-i190Ui4GUR8p1A-zMQ'
pwd = '01g5'

init_url = 'https://pan.baidu.com/share/init?surl=' + surl
html, status = make_request(init_url, data={'pwd': pwd, 'vcode': '', 'vcode_str': ''}, method='POST')
print(f'Init status: {status}')
print(f'Response length: {len(html)}')

# Try to parse as JSON
try:
    d = json.loads(html)
    print(json.dumps(d, ensure_ascii=False, indent=2)[:1000])
except:
    # Check for yunData
    m2 = re.search(r'window\.yunData\s*=\s*({.*?});', html)
    if m2:
        d = json.loads(m2.group(1))
        print(json.dumps(d, ensure_ascii=False, indent=2)[:1000])
    else:
        print('First 1000 chars:')
        print(html[:1000])
