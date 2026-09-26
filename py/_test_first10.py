#!/usr/bin/env python3
import sys, os, subprocess, json, re, time, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'E:\workspace\github\film-tvs')

import openpyxl
wb = openpyxl.load_workbook('res/data_new.xlsx', read_only=True, data_only=True)
entries = []
for sn in wb.sheetnames:
    if sn == 'index': continue
    ws = wb[sn]
    for row in ws.rows:
        if row[0].row == 1: continue
        vals = [c.value for c in row]
        if len(vals) < 10: continue
        link = str(vals[9] or '').strip()
        if 'pan.baidu.com' not in link: continue
        m = re.search(r'pan\.baidu\.com/s/([^\s?&/]+)', link)
        if not m: continue
        pwd_m = re.search(r'[?&]pwd=(\w+)', link)
        entries.append({'shorturl': m.group(1), 'pwd': pwd_m.group(1) if pwd_m else None, 'title': str(vals[2] or '').strip()})
wb.close()

OPENCLI = os.path.expandvars(r'%APPDATA%\npm\node_modules\@jackwener\opencli\dist\src\main.js')
ok = 0
fail = 0
for i, e in enumerate(entries[:10]):
    surl = e['shorturl']
    api_surl = surl[1:] if surl.startswith('1') and len(surl) > 1 else surl
    url = (f'https://pan.baidu.com/share/list?web=5&app_id=250528'
           f'&desc=1&showempty=0&page=1&num=100&order=time'
           f'&shorturl={api_surl}')
    if e['pwd']: url += f'&pwd={e["pwd"]}'
    url += '&root=1&view_mode=1&channel=chunlei&clienttype=0'
    js = f'(function(){{ return fetch("{url}").then(r=>r.json()).then(d=>JSON.stringify(d)); }})()'
    
    t0 = time.time()
    r = subprocess.run(['node', OPENCLI, 'browser', 'work', 'eval', js], capture_output=True, timeout=20)
    raw = r.stdout if len(r.stdout) > 0 else r.stderr
    out = raw.decode('utf-8', errors='replace').strip()
    clean = '\n'.join(l for l in out.split('\n') if not l.startswith('Update available'))
    try:
        data = json.loads(clean)
        errno = data.get('errno')
        lst = data.get('list', [])
        t = time.time() - t0
        status = 'OK' if errno == 0 else f'ERR{errno}'
        print(f'[{i+1}] {e["title"][:20]:20s} {status} items={len(lst)} {t:.1f}s')
        if errno == 0: ok += 1
        else: fail += 1
    except json.JSONDecodeError:
        print(f'[{i+1}] {e["title"][:20]:20s} PARSE_FAIL')
        fail += 1

print(f'\n结果: OK={ok} FAIL={fail} 共{len(entries[:10])}')
