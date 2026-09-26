#!/usr/bin/env python3
import sys, os, subprocess, json
sys.stdout.reconfigure(encoding='utf-8')
OPENCLI = os.path.expandvars(r'%APPDATA%\npm\node_modules\@jackwener\opencli\dist\src\main.js')

# Test known working entry
test_cases = [
    # (surl_with1, pwd, name)
    ('1hPxActzEH1SHQIhsZf-JVw', 't05z', '老男孩'),  # from data_new pwd=t05z
    ('1hSkb_3N5jFzEqXTqh3wXfQ', '4210', '天启Z'),  # from data_new pwd=4210
    ('1EBRzUmXqR7Br3bO26s83fg', '85gn', '世奇SP'),  # failed earlier
]

for surl_with1, pwd, name in test_cases:
    api_surl = surl_with1[1:]
    url = (f'https://pan.baidu.com/share/list?web=5&app_id=250528'
           f'&desc=1&showempty=0&page=1&num=100&order=time'
           f'&shorturl={api_surl}&pwd={pwd}'
           f'&root=1&view_mode=1&channel=chunlei&clienttype=0')
    js = f'(function(){{ return fetch("{url}").then(r=>r.json()).then(d=>JSON.stringify(d)); }})()'
    
    r = subprocess.run(['node', OPENCLI, 'browser', 'work', 'eval', js], capture_output=True, timeout=20)
    raw = r.stdout if len(r.stdout) > 0 else r.stderr
    out = raw.decode('utf-8', errors='replace').strip()
    clean = '\n'.join(l for l in out.split('\n') if not l.startswith('Update available'))
    try:
        data = json.loads(clean)
        print(f'{name}: errno={data.get("errno")} msg={data.get("show_msg","")} items={len(data.get("list",[]))}')
    except json.JSONDecodeError:
        print(f'{name}: PARSE_FAIL ({clean[:100]})')
