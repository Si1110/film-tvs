import sys, json, re, os, urllib.parse, urllib.request, http.cookiejar
sys.stdout.reconfigure(encoding='utf-8')

BDUSS = os.environ.get('BDUSS', '')
STOKEN = os.environ.get('STOKEN', '')

# Use cookiejar for proper session
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Set BDUSS and STOKEN cookies
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
        resp = opener.open(req, timeout=20)
        raw = resp.read()
        text = raw.decode('utf-8', errors='replace')
        print(f'  Status: {resp.status}, URL: {resp.url}')
        return text, resp.status
    except urllib.request.HTTPError as e:
        raw = e.read()
        text = raw.decode('utf-8', errors='replace')
        print(f'  Status error: {e.code}, URL: {e.url}')
        return text, e.code
    except Exception as e:
        print(f'  Error: {e}')
        return '', 0

# First, get pan.baidu.com homepage to establish session
print("Step 1: Get homepage")
html, status = fetch('https://pan.baidu.com/')
print(f'  Cookies: {len(cj)}')
m = re.search(r'bdstoken[":=\s]+([a-f0-9]+)', html[:10000])
bdstoken = m.group(1) if m else ''
print(f'  bdstoken: {bdstoken}')

# Try different share URL patterns
surl = '1gKy-i190Ui4GUR8p1A-zMQ'
pwd = '01g5'

# Pattern 1: /s/1{surl} (direct share page)
print(f"\nStep 2: Try /s/1{surl}")
html, status = fetch(f'https://pan.baidu.com/s/1{surl}')
if status == 404:
    # Pattern 2: Add ?pwd=
    print(f"\nStep 2b: /s/1{surl}?pwd={pwd}")
    html, status = fetch(f'https://pan.baidu.com/s/1{surl}?pwd={pwd}')

# Pattern 3: /share/init with POST  
print(f"\nStep 3: /share/init POST")
html, status = fetch(f'https://pan.baidu.com/share/init?surl={surl}',
                     data={'pwd': pwd, 'vcode': '', 'vcode_str': ''})

# Pattern 4: Different share URL format
print(f"\nStep 4: Try without /1/ prefix")
html2, status2 = fetch(f'https://pan.baidu.com/s/{surl}')
print(f'  Status: {status2}')

# Pattern 5: Try share page with UK embedded
# First find shareid and uk from /s/1 page
# Check if we got any yunData or file data anywhere
print(f"\nStep 5: Try another share that might work")
# Try a simpler share link
test_share = '1nZMvC1m24zTfRd6U9jYMrg'  # 暗河传 - no password
html, status = fetch(f'https://pan.baidu.com/s/1{test_share}')
if status == 200:
    # Look for data
    m = re.search(r'window\.yunData\s*=\s*({.*?});', html)
    if m:
        d = json.loads(m.group(1))
        print(f'  yunData found: {json.dumps(d, ensure_ascii=False, indent=2)[:1000]}')
    else:
        # Look for any JSON data
        for pat in [r'file_list[\s\S]{0,10}?=\s*(\[[\s\S]*?\])\s*;',
                     r'data\s*:\s*(\[[\s\S]*?\])\s*,\s*errno']:
            m2 = re.search(pat, html)
            if m2:
                print(f'  found data pattern: {m2.group(0)[:200]}')
                break
        else:
            # Print short sample
            # Look for share info in HTML
            for keyword in ['shareid', 'share_id', '"uk"', 'randsk']:
                idx = html.find(keyword)
                if idx > -1:
                    print(f'  Found "{keyword}" at pos {idx}: ...{html[max(0,idx-20):idx+80]}...')
