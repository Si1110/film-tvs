#!/usr/bin/env python3
"""小批量测试百度网盘目录抓取"""
import sys, os, json, subprocess, time, html, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

PROJ = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(PROJ, 'res', 'dirs')
OPENCLI_MAIN = os.path.expandvars(r'%APPDATA%\npm\node_modules\@jackwener\opencli\dist\src\main.js')

def call_api(shorturl, pwd=None, dir_path=None, page=1, num=100):
    url = (f'https://pan.baidu.com/share/list?web=5&app_id=250528'
           f'&desc=1&showempty=0&page={page}&num={num}&order=time'
           f'&shorturl={shorturl}')
    if pwd:
        url += f'&pwd={pwd}'
    if dir_path:
        url += f'&dir={urllib.parse.quote(dir_path, safe="")}'
    else:
        url += '&root=1'
    url += '&view_mode=1&channel=chunlei&clienttype=0'

    js = f'(function(){{ return fetch("{url}").then(r=>r.json()).then(d=>JSON.stringify(d)); }})()'
    cmd = ['node', OPENCLI_MAIN, 'browser', 'work', 'eval', js]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=20)
        raw = r.stdout if len(r.stdout) > 0 else r.stderr
        if len(raw) == 0:
            return None
        try:
            out = raw.decode('utf-8').strip()
        except:
            out = raw.decode('gbk', errors='replace').strip()
        lines = [l for l in out.split('\n') if not l.startswith('Update available')]
        clean = '\n'.join(lines)
        if clean.startswith('{'):
            return json.loads(clean)
        return None
    except Exception as e:
        print(f'  ERROR: {e}')
        return None

def fetch_recursive(shorturl, pwd, dir_path=None):
    all_items = []
    page = 1
    while True:
        data = call_api(shorturl, pwd, dir_path, page, 100)
        if not data or data.get('errno') != 0:
            break
        entries = data.get('list', [])
        if not entries:
            break
        all_items.extend(entries)
        if len(entries) < 100:
            break
        page += 1

    for item in all_items:
        if item.get('isdir') == '1':
            sub_path = item.get('path', '')
            children = fetch_recursive(shorturl, pwd, sub_path)
            if children:
                item['_children'] = children
    return all_items

def save_html(shorturl, name, items):
    out_path = os.path.join(DATA_DIR, f'baidu_{shorturl}.html')
    lines = ['<!DOCTYPE html><html lang="zh-CN">']
    lines.append(f'<head><meta charset="UTF-8"><title>{html.escape(name)} - 目录</title>')
    lines.append('<style>body{font-family:"Microsoft YaHei",sans-serif;background:#1a1a2e;padding:20px;font-size:14px;line-height:1.8;}')
    lines.append('a{color:#4fc3f7;text-decoration:none;}a:hover{text-decoration:underline;}')
    lines.append('.folder{color:#ffd700;margin-bottom:4px;}.file{color:#ccc;margin-left:20px;}')
    lines.append('.size{color:#888;font-size:12px;margin-left:10px;}</style></head><body><div class="tree">')
    for item in items:
        isdir = item.get('isdir') == '1'
        item_name = item.get('server_filename', '?')
        icon = '📁' if isdir else '📄'
        cls = 'folder' if isdir else 'file'
        children = item.get('_children', [])
        if children:
            lines.append(f'<div class="{cls}">{icon} {html.escape(item_name)} ({len(children)} 项)</div><div style="margin-left:24px;">')
            for child in children:
                c_name = child.get('server_filename', '?')
                lines.append(f'<div class="file">📄 {html.escape(c_name)}</div>')
            lines.append('</div>')
        else:
            lines.append(f'<div class="{cls}">{icon} {html.escape(item_name)}</div>')
    total = sum(1 + len(item.get('_children', [])) for item in items)
    lines.append(f'</div><hr><p class="size">共 {total} 项</p></body></html>')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return out_path

# 测试
test_cases = [
    ('hPxActzEH1SHQIhsZf-JVw', None, '老男孩'),
    ('hB7hrM45Pg7_hjbSGfOG_A', '3416', '变形金刚'),
    ('hSkb_3N5jFzEqXTqh3wXfQ', None, '天启Z'),
]

for shorturl, pwd, name in test_cases:
    print(f'\n=== {name} ({shorturl}) ===')
    start = time.time()
    items = fetch_recursive(shorturl, pwd)
    elapsed = time.time() - start
    flat_n = len(items)
    sub_n = sum(len(item.get('_children', [])) for item in items)
    print(f'根目录: {flat_n} 项, 子目录: {sub_n} 项, 耗时: {elapsed:.1f}s')
    for item in items:
        sig = '📁' if item.get('isdir') == '1' else '📄'
        print(f'  {sig} {item["server_filename"]}')
        for child in item.get('_children', []):
            print(f'    📄 {child["server_filename"]}')
    path = save_html(shorturl, name, items)
    print(f'  保存: {path}')
