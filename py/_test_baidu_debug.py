#!/usr/bin/env python3
import sys, os, json, subprocess, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

shorturl = 'hPxActzEH1SHQIhsZf-JVw'
pwd = None

url = (f'https://pan.baidu.com/share/list?web=5&app_id=250528'
       f'&desc=1&showempty=0&page=1&num=100&order=time'
       f'&shorturl={shorturl}')
if pwd:
    url += f'&pwd={pwd}'
url += '&root=1&view_mode=1&channel=chunlei&clienttype=0'

js = f'(function(){{ return fetch("{url}").then(r=>r.json()).then(d=>JSON.stringify(d)); }})()'
print(f'JS length: {len(js)}')
print(f'JS: {js[:200]}...')

cmd = ['node', os.path.expandvars(r'%APPDATA%\npm\node_modules\@jackwener\opencli\dist\src\main.js'), 'browser', 'work', 'eval', js]
r = subprocess.run(cmd, capture_output=True, timeout=20)
print(f'Return code: {r.returncode}')
print(f'stdout bytes: {len(r.stdout)}')
print(f'stderr bytes: {len(r.stderr)}')
raw = r.stdout if len(r.stdout) > 0 else r.stderr
if len(raw) == 0:
    print('EMPTY OUTPUT - both stdout and stderr empty')
    exit()
try:
    out = raw.decode('utf-8').strip()
except:
    out = raw.decode('gbk', errors='replace').strip()

# Print raw output truncated
print(f'\nRaw output ({len(out)} chars):')
print(out[:500])
print('...')
print(out[-500:] if len(out) > 500 else '')

lines = [l for l in out.split('\n') if not l.startswith('Update available')]
clean = '\n'.join(lines)
print(f'\nClean output starts with: {clean[:100]}')

try:
    data = json.loads(clean)
    print(f'\nerrno: {data.get("errno")}')
    print(f'list: {json.dumps(data.get("list"), ensure_ascii=False, indent=2)[:500]}')
except json.JSONDecodeError as e:
    print(f'\nJSON parse error: {e}')
    # Show the problematic part
    print(f'Around error: ...{clean[max(0,e.pos-50):e.pos+50]}...')
