import sys, json, re, os
sys.stdout.reconfigure(encoding='utf-8')
import requests

BDUSS = os.environ.get('BDUSS', '')
STOKEN = os.environ.get('STOKEN', '')
print(f"BDUSS: {'set' if BDUSS else 'not set'}, STOKEN: {'set' if STOKEN else 'not set'}")

s = requests.Session()
s.cookies.set('BDUSS', BDUSS)
s.cookies.set('STOKEN', STOKEN)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://pan.baidu.com/',
}

# Try to get bdstoken from pan.baidu.com home
r = s.get('https://pan.baidu.com/', headers=headers, timeout=15, verify=False)
print('Home status:', r.status_code)

# Debug: save response to inspect
with open('C:/Users/DELL/AppData/Local/Temp/baidu_home.html', 'w', encoding='utf-8') as f:
    f.write(r.text[:10000])

# Try to extract bdstoken - look for various patterns
patterns = [
    r'bdstoken[":=\s]+([a-f0-9]+)',
    r'bdstoken["\']?\s*[:=]\s*["\']([a-f0-9]+)',
    r'"bdstoken"\s*:\s*"([^"]+)"',
    r"bdstoken\s*=\s*'([^']+)'",
]
for pat in patterns:
    m = re.search(pat, r.text[:5000])
    if m:
        print(f"Found bdstoken: {m.group(1)}")
        break
else:
    print("No bdstoken found")
    # Print first 2000 chars for debug
    print("First 2000 chars:")
    print(r.text[:2000])
