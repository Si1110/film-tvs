#!/usr/bin/env python3
"""Batch copy covers from 缺失封面 to res/movie-covers/ and update Excel."""
import os, sys, shutil, openpyxl, re
sys.stdout.reconfigure(encoding='utf-8')

cover_root = r'F:\1、自媒体\3、网站\影视\缺失封面'
xlsx = 'res/data_new.xlsx'
dest_dir = 'res/movie-covers'

# Build cover index
all_covers = {}
for dirpath, dirnames, filenames in os.walk(cover_root):
    for f in filenames:
        if not f.endswith(('.webp', '.jpg', '.png', '.jpeg')):
            continue
        name_no_ext = os.path.splitext(f)[0]
        all_covers[name_no_ext] = os.path.join(dirpath, f)

# Excel title -> cover name in 缺失封面 (name without extension)
cover_map = {
    '电锯惊魂(Saw,2004)': '电锯惊魂',
    '电锯惊魂10 (Saw X,2023)': '电锯惊魂10',
    '海王(Aquaman, 2018)': '海王',
    '海王2:失落的王国(Aquaman and the Lost Kingdom, 2023)': '海王2',
    '月光光心慌慌7': '月光光心慌慌',
    '月光光心慌慌9/索命万圣节': '月光光心慌慌9',
    '月光光心慌慌10/新万圣节2': '月光光心慌慌10',
    '月光光心慌慌12：杀戮': '月光光心慌慌12',
    '致命录像带3': '致命录像带3：病毒',
    '哥斯拉（2000)': '哥斯拉2000',
    '哥斯拉大战超翔龙 (2000)': '哥斯拉大战超翔龙',
    '哥斯拉再战机械哥斯拉 (2002)': '哥斯拉再战机械哥斯拉',
    '哥斯拉×摩斯拉×机械哥斯拉 (2003)': '哥斯拉×摩斯拉×机械哥斯拉',
    '哥斯拉之终极战役 (2004)': '哥斯拉之终极战役',
    '哥斯拉 (1984)': '哥斯拉(1984)',
    '哥斯拉VS碧奥兰蒂 (1989)': '哥斯拉VS碧奥兰蒂',
    '哥斯拉vs王者基多拉 (1991)': '哥斯拉vs王者基多拉',
    '哥斯拉vs摩斯拉 (1992)': '哥斯拉vs摩斯拉',
    '哥斯拉vs机械哥斯拉 (1993)': '哥斯拉vs机械哥斯拉',
    '哥斯拉vs太空哥斯拉 (1994)': '哥斯拉vs太空哥斯拉',
    '哥斯拉vs戴斯特洛伊亚 (1995)': '哥斯拉vs戴斯特洛伊亚',
    '哥斯拉的反击（1955）': '哥斯拉的反击',
    '金刚对哥斯拉（1962）': '金刚对哥斯拉',
    '战龙哥斯拉之三大怪兽（1964）': '战龙哥斯拉之三大怪兽',
    '哥斯拉之怪兽大战争（1965）': '哥斯拉之怪兽大战争',
    '哥斯拉·伊比拉·摩斯拉：南海大决斗（1966）': '哥斯拉·伊比拉·摩斯拉：南海大决斗',
    '怪兽岛决战：哥斯拉之子（1967）': '怪兽岛决战：哥斯拉之子',
    '怪兽总进击（1968）': '怪兽总进击',
    '哥斯拉·迷你拉·加巴拉：全体怪兽大进击（1969）': '哥斯拉·迷你拉·加巴拉：全体怪兽大进击',
    '哥斯拉对黑多拉（1971）': '哥斯拉对黑多拉',
    '战龙哥斯拉之决战宇宙魔龙 地球攻撃命令（1972）': '战龙哥斯拉之决战宇宙魔龙 地球攻撃命令',
    '哥斯拉对美加洛（1973）': '哥斯拉对美加洛',
    '哥斯拉对机械哥斯拉（1974）': '哥斯拉对机械哥斯拉',
    '哥斯拉之机械哥斯拉的反击（1975）': '哥斯拉的反击',
    '玻璃樽(未删减版)': '玻璃樽',
    '醒目仔蛊惑招/肥龙功夫精': '肥龙功夫精',
    '天若有情/追梦人': '天若有情',
    '五亿探长雷洛传2：父子情仇': '五亿探长雷洛传Il父子情仇',
    '宇宙追缉令/救世主': '宇宙追缉令',
    '龙潭虎穴/致命摇篮': '龙潭虎穴',
    '俠盜高飛': '俠盜高飛 (1992)',
    '大灵通': '大灵通1992',
    '哗鬼住正隔篱/有鬼住在隔壁': '哗鬼住正隔篱',
    '张保仔/怒海侠盗 (1994)': '张保仔',
    '執法先鋒(不死版結局)': '執法先鋒',
    '德州电锯杀人狂 (2003)': '德州电锯杀人狂(2003)',
    '阿凡达': '阿凡达 Avatar (2009)',
    '阿凡达：水之道': '阿凡达：水之道(2022)',
    '芝士火腿 / 咖喱辣椒3': '芝士火腿',
    '女高怪谈 1：死亡教室': '女高怪谈1：死亡教室',
    '女高怪谈 2：交换日记': '女高怪谈2：交换日记',
    '女高怪谈 3：狐狸阶梯': '女高怪谈3：狐狸阶梯',
    '女高怪谈 4：声音': '女高怪谈4：声音',
    '女高怪谈 5：结伴自杀': '女高怪谈5：结伴自杀',
    # Still no cover:
    # '007之金刚钻 Diamonds Are Forever (1971)': None,
    # '德州电锯杀人狂前传 (2006)': None,
    # '最佳拍档3：女皇密令': None,
    # '王牌特工【系列合集】': None,
    # '长江七号': None,
}

copied = 0
wb = openpyxl.load_workbook(xlsx)

for sn in wb.sheetnames:
    if sn == 'index':
        continue
    ws = wb[sn]
    for row in ws.rows:
        if row[0].row == 1:
            continue
        vals = [c.value for c in row]
        if len(vals) < 3:
            continue
        title = str(vals[2] or '').strip()
        if not title or title not in cover_map:
            continue
        cover_name = cover_map[title]
        if cover_name not in all_covers:
            print(f'[SKIP] {title}: "{cover_name}" not found in 缺失封面')
            continue

        src = all_covers[cover_name]
        src_ext = os.path.splitext(src)[1]

        # Sanitize dest filename: replace / \ : with safe chars
        safe_title = title.replace('/', '_').replace('\\', '_').replace(':', '：')
        dest = os.path.join(dest_dir, f'{safe_title}{src_ext}')

        # Copy file if not exists
        if not os.path.exists(dest):
            shutil.copy2(src, dest)
            print(f'[COPY] {os.path.basename(src)} -> {dest}')
        else:
            print(f'[EXISTS] {dest}')

        # Update Excel column 2 (封面图片路径)
        cover_path = f'../res/movie-covers/{safe_title}{src_ext}'
        ws.cell(row=row[0].row, column=2).value = cover_path
        print(f'  Excel: col2 = {cover_path}')
        copied += 1

wb.save(xlsx)
wb.close()
print(f'\nTotal copied/updated: {copied}')
print(f'Still missing covers: 5 (007之金刚钻, 德州电锯杀人狂前传, 最佳拍档3, 王牌特工合集, 长江七号)')
