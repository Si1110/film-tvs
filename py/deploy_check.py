#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一站式预部署验证脚本

按顺序运行所有检查：
1. HTML 生成（generate_html.py）
2. 排序验证 + 孤立主题检测 + HTML 顺序检测（verify_sort.py）
3. BOM 污染检测
4. CSS Grid 布局正确性检测

用法：python py/deploy_check.py

退出码：0 = 全通过，1 = 有错误
"""

import os
import sys
import subprocess
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTIONS_DIR = os.path.join(PROJECT_ROOT, 'sections')

PASS = '[PASS]'
FAIL = '[FAIL]'
WARN = '[WARN]'

checks_passed = 0
checks_failed = 0
total_checks = 0


def run_step(name, command, cwd=None):
    global checks_passed, checks_failed, total_checks
    total_checks += 1
    print(f"\n  {'='*56}")
    print(f"  步骤 {total_checks}: {name}")
    print(f"  {'='*56}")

    result = subprocess.run(command, shell=True, cwd=cwd or PROJECT_ROOT,
                            capture_output=True)
    raw = (result.stdout + result.stderr)
    out = raw.decode('utf-8', errors='replace').strip()

    if result.returncode == 0:
        checks_passed += 1
        print(f"  {PASS} 通过")
    else:
        checks_failed += 1
        print(f"  {FAIL} 失败 (exit code {result.returncode})")

    # Print output (tail only for long output)
    if out:
        lines = out.split('\n')
        if len(lines) > 20:
            print(f"     (输出过长，显示最后 20 行)")
            for line in lines[-20:]:
                print(f"     {line.encode('utf-8', errors='replace').decode('utf-8')}")
        else:
            for line in lines:
                print(f"     {line.encode('utf-8', errors='replace').decode('utf-8')}")

    return result.returncode == 0


def check_bom():
    """Check all section HTML files for BOM contamination."""
    global checks_passed, checks_failed, total_checks
    total_checks += 1
    print(f"\n  {'='*56}")
    print(f"  步骤 {total_checks}: BOM 污染检测")
    print(f"  {'='*56}")

    if not os.path.isdir(SECTIONS_DIR):
        print(f"  {FAIL} sections/ 目录不存在")
        checks_failed += 1
        return False

    html_files = [f for f in os.listdir(SECTIONS_DIR)
                  if f.startswith('section-') and f.endswith('.html')]

    found_bom = False
    for hf in html_files:
        path = os.path.join(SECTIONS_DIR, hf)
        with open(path, 'rb') as f:
            content = f.read()
        bom_count = content.count(b'\xef\xbb\xbf')
        if bom_count > 0:
            print(f"  {FAIL} {hf}: 发现 {bom_count} 个 BOM 头")
            found_bom = True

    if found_bom:
        checks_failed += 1
        return False
    else:
        print(f"  {PASS} 所有文件无 BOM")
        checks_passed += 1
        return True


def check_grid_layout():
    """Verify the section HTML uses CSS Grid (not Flexbox) for card layout."""
    global checks_passed, checks_failed, total_checks
    total_checks += 1
    print(f"\n  {'='*56}")
    print(f"  步骤 {total_checks}: CSS Grid 布局正确性检测")
    print(f"  {'='*56}")

    if not os.path.isdir(SECTIONS_DIR):
        print(f"  {FAIL} sections/ 目录不存在")
        checks_failed += 1
        return False

    html_files = [f for f in os.listdir(SECTIONS_DIR)
                  if f.startswith('section-') and f.endswith('.html')]

    grid_issues = []
    for hf in html_files:
        path = os.path.join(SECTIONS_DIR, hf)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check card-grid uses display: grid
        grid_style = re.search(r'\.card-grid\s*\{[^}]*display:\s*grid[^}]*\}', content)
        if not grid_style:
            grid_issues.append(f"{hf}: .card-grid 未使用 display: grid")

        # Check for row g-3 class on card-grid (old Flexbox layout)
        if 'class="card-grid row g-3"' in content or 'class="row g-3 card-grid"' in content:
            grid_issues.append(f"{hf}: .card-grid 使用了 row g-3 (Flexbox)，应使用 CSS Grid")

        # Check card count matches expected pattern
        card_count = len(re.findall(r'class="card-grid', content))
        if card_count == 0:
            grid_issues.append(f"{hf}: 未找到 .card-grid 容器")

    if grid_issues:
        print(f"  {FAIL} 发现 {len(grid_issues)} 个 CSS Grid 问题:")
        for issue in grid_issues:
            print(f"     - {issue}")
        checks_failed += 1
        return False
    else:
        print(f"  {PASS} 所有页面使用 CSS Grid (3列布局)")
        checks_passed += 1
        return True


def main():
    print(f"\n{'='*60}")
    print(f"  FilmTVs 预部署验证")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    ok = True
    ok &= run_step("HTML 生成", f"{sys.executable} py/generate_html.py")
    ok &= run_step("排序验证", f"{sys.executable} py/verify_sort.py")
    ok &= check_bom()
    ok &= check_grid_layout()

    print(f"\n{'='*60}")
    if checks_failed == 0:
        print(f"  {PASS} 全部 {total_checks} 项检查通过！可以部署。")
    else:
        print(f"  {FAIL} {checks_failed}/{total_checks} 项检查失败，请修复后重试。")
    print(f"{'='*60}")

    return 0 if checks_failed == 0 else 1


if __name__ == '__main__':
    from datetime import datetime
    sys.exit(main())
