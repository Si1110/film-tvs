#!/usr/bin/env python3
"""批量抓取百度网盘目录 - 通过浏览器 API"""
import sys, os, json, subprocess, time, html, urllib.parse, re
sys.stdout.reconfigure(encoding='utf-8')

PROJ = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(PROJ, 'res', 'dirs')
XLSX_PATH = os.path.join(PROJ, 'res', 'data_new.xlsx')
OPENCLI_MAIN = os.path.expandvars(r'%APPDATA%\npm\node_modules\@jackwener\opencli\dist\src\main.js')
PROGRESS_FILE = os.path.join(PROJ, 'py', '.baidu_batch_progress.json')

def call_api(shorturl, pwd=None, dir_path=None, page=1, num=100):
    api_surl = shorturl[1:] if shorturl.startswith('1') and len(shorturl) > 1 else shorturl
    url = (f'https://pan.baidu.com/share/list?web=5&app_id=250528'
           f'&desc=1&showempty=0&page={page}&num={num}&order=time'
           f'&shorturl={api_surl}')
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
        r = subprocess.run(cmd, capture_output=True, timeout=25)
        raw = r.stdout if len(r.stdout) > 0 else r.stderr
        if len(raw) == 0:
            return None
        out = raw.decode('utf-8', errors='replace').strip()
        clean = '\n'.join(l for l in out.split('\n') if not l.startswith('Update available'))
        if clean.startswith('{'):
            return json.loads(clean)
        return None
    except:
        return None

def fetch_recursive(shorturl, pwd, dir_path=None, depth=0):
    if depth > 6:
        return []
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
            children = fetch_recursive(shorturl, pwd, sub_path, depth + 1)
            if children:
                item['_children'] = children
    return all_items

def generate_html(shorturl, title, items):
    name = title or '目录'
    if not items:
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>{html.escape(name)} - 目录</title>
<style>
body {{ font-family: 'Microsoft YaHei', sans-serif; background: #1a1a2e; padding: 20px; font-size: 14px; line-height: 1.8; }}
a {{ color: #4fc3f7; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.placeholder {{ color: #888; text-align: center; margin-top: 40px; }}
</style>
</head><body>
<div class="placeholder">
  <div style="font-size: 18px; color: #ffd700;">📁 {html.escape(name)}</div>
  <div style="margin-top: 10px; color: #666;">该资源目录请前往百度网盘查看</div>
  <div style="margin-top: 15px;">
    <a href="https://pan.baidu.com/s/{shorturl}" target="_blank" style="display: inline-block; padding: 10px 24px; background: #4fc3f7; color: #fff; border-radius: 6px; text-decoration: none;">打开百度网盘</a>
  </div>
</div>
</body></html>'''

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
    return '\n'.join(lines)

def extract_baidu_entries():
    import openpyxl
    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True, data_only=True)
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
            title = str(vals[2] or '').strip()
            entries.append({
                'shorturl': m.group(1),
                'pwd': pwd_m.group(1) if pwd_m else None,
                'title': title,
                'sheet': sn,
            })
    wb.close()
    return entries

def main():
    print('读取 data_new.xlsx ...')
    all_entries = extract_baidu_entries()
    print(f'找到 {len(all_entries)} 个百度条目')

    # 过滤：跳过已有真实目录的
    to_process = []
    for e in all_entries:
        out_path = os.path.join(DATA_DIR, f'baidu_{e["shorturl"]}.html')
        if os.path.exists(out_path):
            with open(out_path, 'r', encoding='utf-8') as f:
                c = f.read()
            if ('📁' in c or '📄' in c) and '打开百度网盘' not in c:
                continue  # 已有真实目录
        to_process.append(e)

    print(f'需处理: {len(to_process)} 个')

    # 重置浏览器会话（关闭旧的，打开新的）
    print('重置浏览器会话...')
    subprocess.run(['node', OPENCLI_MAIN, 'browser', 'work', 'close'], capture_output=True, timeout=10)
    time.sleep(1)
    r = subprocess.run(['node', OPENCLI_MAIN, 'browser', 'work', 'open', 'https://pan.baidu.com'], capture_output=True, timeout=30)
    print(f'新会话: {r.stdout.decode("utf-8", errors="replace")[:100]}')

    cap_count = 0  # 需要验证码（errno=-9）
    ok_count = 0   # 成功
    fail_count = 0 # 其他错误
    total = len(to_process)

    for i, e in enumerate(to_process):
        shorturl = e['shorturl']
        pwd = e['pwd']
        title = e['title'][:25]
        out_path = os.path.join(DATA_DIR, f'baidu_{shorturl}.html')

        sys.stdout.write(f'[{i+1}/{total}] {shorturl[:15]} ({title}) ... ')
        sys.stdout.flush()

        start_t = time.time()

        # 先获取根目录
        data = call_api(shorturl, pwd)
        elapsed = time.time() - start_t

        if not data:
            html_content = generate_html(shorturl, e['title'], [])
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f'TIMEOUT ({elapsed:.1f}s)')
            fail_count += 1
            continue

        errno = data.get('errno')
        if errno != 0:
            if errno == -9:
                print(f'CAPTCHA ({elapsed:.1f}s)')
                cap_count += 1
            else:
                print(f'ERR{errno} ({elapsed:.1f}s)')
                fail_count += 1
            # 保持已有 placeholder 文件不变（不覆盖）
            continue

        # errno=0 → 递归获取完整目录
        items = fetch_recursive(shorturl, pwd)
        elapsed2 = time.time() - start_t

        html_content = generate_html(shorturl, e['title'], items)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        flat_n = len(items)
        sub_n = sum(len(item.get('_children', [])) for item in items)
        print(f'OK ({flat_n}+{sub_n}={flat_n+sub_n} items, {elapsed2:.1f}s)')
        ok_count += 1

        # 每 15 个休息一下
        if i % 15 == 14 and i < total - 1:
            time.sleep(1)

    print(f'\n完成! 成功={ok_count} 需验证码={cap_count} 其他失败={fail_count} 总计={total}')

if __name__ == '__main__':
    main()
