#!/usr/bin/env python3
import sys, os, subprocess, json
sys.stdout.reconfigure(encoding='utf-8')
OPENCLI = os.path.expandvars(r'%APPDATA%\npm\node_modules\@jackwener\opencli\dist\src\main.js')

# Test with one failed entry
surl_with1 = '1EBRzUmXqR7Br3bO26s83fg'
pwd = '85gn'
api_surl = surl_with1[1:]

url = (f'https://pan.baidu.com/share/list?web=5&app_id=250528'
       f'&desc=1&showempty=0&page=1&num=100&order=time'
       f'&shorturl={api_surl}&pwd={pwd}'
       f'&root=1&view_mode=1&channel=chunlei&clienttype=0')

js = f'(function(){{ return fetch("{url}").then(r=>r.json()).then(d=>JSON.stringify(d)); }})()'
print(f'API URL: {url[:150]}...')
r = subprocess.run(['node', OPENCLI, 'browser', 'work', 'eval', js], capture_output=True, timeout=20)
raw = r.stdout if len(r.stdout) > 0 else r.stderr
out = raw.decode('utf-8', errors='replace').strip()
clean = '\n'.join(l for l in out.split('\n') if not l.startswith('Update available'))
print(f'Response: {clean[:300]}')
