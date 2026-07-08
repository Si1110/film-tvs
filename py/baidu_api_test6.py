import sys, json, re, os, urllib.parse, urllib.request, http.cookiejar
sys.stdout.reconfigure(encoding='utf-8')

BDUSS = os.environ.get('BDUSS', '')
STOKEN = os.environ.get('STOKEN', '')

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://pan.baidu.com/',
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
        print(f'  Error: {e.code}')
        return text, e.code
    except Exception as e:
        print(f'  Error: {e}')
        return '', 0

def parse_data(html):
    """Extract share data from page HTML"""
    # Try yunData
    m = re.search(r'window\.yunData\s*=\s*({.*?})\s*;', html)
    if m:
        try:
            d = json.loads(m.group(1))
            return d
        except:
            pass
    
    # Try various patterns
    for key in ['shareid', 'uk', 'sekey', 'randsk', 'bdstoken']:
        m = re.search(rf'["\']{key}["\']\s*[:=]\s*["\']?([^"\'&\s,}}]+)["\']?', html)
        if m:
            print(f'  {key}: {m.group(1)[:100]}')
    
    # Look for JSON anywhere in script tags
    for m in re.finditer(r'<script[^>]*>([\s\S]*?)</script>', html):
        script = m.group(1)
        if 'yunData' in script or 'shareid' in script or 'file_list' in script:
            print(f'  Script with data found (len={len(script)})')
            # Try to extract JSON object
            for pat in [r'({\s*"errno"[\s\S]*?})\s*;',
                        r'(\[.*?\])\s*;']:
                m2 = re.search(pat, script)
                if m2:
                    try:
                        d = json.loads(m2.group(1))
                        print(f'  Parsed: {json.dumps(d, ensure_ascii=False)[:500]}')
                        return d
                    except:
                        pass
    
    return None

# Step 1: Establish session
print("Step 1: Get homepage")
html, _ = fetch('https://pan.baidu.com/')

# Step 2: Fetch the share page directly
surl = '1gKy-i190Ui4GUR8p1A-zMQ'
pwd = '01g5'

print(f"\nStep 2: Fetch /s/{surl}")
html, s = fetch(f'https://pan.baidu.com/s/{surl}')
print(f'  Response length: {len(html)}')

if s == 200:
    data = parse_data(html)
    if data:
        print(f'\nParsed data: {json.dumps(data, ensure_ascii=False, indent=2)[:2000]}')
    else:
        print('  Could not find data, saving HTML for inspection')
        with open('C:/Users/DELL/AppData/Local/Temp/baidu_share.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print('  Saved to Temp/baidu_share.html')
        # Print part of the HTML to see structure
        for i, keyword in enumerate(['yunData', 'shareid', 'file_list', 'errno', 'data-item']):
            idx = html.find(keyword)
            if idx > -1:
                print(f'  Found "{keyword}" at {idx}: ...{html[max(0,idx-30):idx+150]}...')
