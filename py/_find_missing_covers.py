#!/usr/bin/env python3
"""Browse the 缺失封面 directory and find matching covers for empty-path cards."""
import os, sys, openpyxl
sys.stdout.reconfigure(encoding='utf-8')

root = r'F:\1、自媒体\3、网站\影视\缺失封面'
xlsx = 'res/data_new.xlsx'

# List all cover files
all_covers = {}
for dirpath, dirnames, filenames in os.walk(root):
    rel_dir = os.path.relpath(dirpath, root)
    for f in filenames:
        if f.endswith(('.webp', '.jpg', '.png', '.jpeg')):
            name_no_ext = os.path.splitext(f)[0]
            all_covers[name_no_ext] = os.path.join(dirpath, f)

print(f'Total cover files in 缺失封面: {len(all_covers)}')

# Show some examples organized by subdirectory
for dirpath, dirnames, filenames in os.walk(root):
    rel = os.path.relpath(dirpath, root)
    count = len([f for f in filenames if f.endswith(('.webp','.jpg','.png'))])
    if count > 0:
        print(f'  {rel}: {count} files')
        for f in filenames[:5]:
            if f.endswith(('.webp','.jpg','.png')):
                print(f'    {f}')
        if count > 5:
            print(f'    ...({count-5} more)')

print()

# Now find matching covers for the empty-path cards
wb = openpyxl.load_workbook(xlsx, data_only=True)

# User's problem cards
problem_titles = [
    '王牌特工【系列合集】', '德州电锯杀人狂 (2003)', '德州电锯杀人狂前传 (2006)',
    '007之金刚钻 Diamonds Are Forever (1971)', '阿凡达', '阿凡达：水之道',
    '女高怪谈 1：死亡教室', '女高怪谈 2：交换日记', '女高怪谈 3：狐狸阶梯',
    '女高怪谈 4：声音', '女高怪谈 5：结伴自杀',
    '芝士火腿 / 咖喱辣椒3', '最佳拍档3：女皇密令', '執法先鋒(不死版結局)',
    '张保仔/怒海侠盗 (1994)', '哗鬼住正隔篱/有鬼住在隔壁', '大灵通',
    '俠盜高飛', '龙潭虎穴/致命摇篮', '宇宙追缉令/救世主',
    '五亿探长雷洛传2：父子情仇', '天若有情/追梦人', '醒目仔蛊惑招/肥龙功夫精',
    '长江七号', '玻璃樽(未删减版)',
    '哥斯拉之机械哥斯拉的反击（1975）', '哥斯拉对机械哥斯拉（1974）',
    '哥斯拉对美加洛（1973）', '战龙哥斯拉之决战宇宙魔龙 地球攻撃命令（1972）',
    '哥斯拉对黑多拉（1971）', '哥斯拉·迷你拉·加巴拉：全体怪兽大进击（1969）',
    '怪兽总进击（1968）', '怪兽岛决战：哥斯拉之子（1967）',
    '哥斯拉·伊比拉·摩斯拉：南海大决斗（1966）', '哥斯拉之怪兽大战争（1965）',
    '战龙哥斯拉之三大怪兽（1964）', '摩斯拉决战哥斯拉 (1964)', '金刚对哥斯拉（1962）',
    '哥斯拉的反击（1955）', '哥斯拉 (1984)', '哥斯拉VS碧奥兰蒂 (1989)',
    '哥斯拉vs太空哥斯拉 (1994)', '哥斯拉vs戴斯特洛伊亚 (1995)',
    '哥斯拉vs摩斯拉 (1992)', '哥斯拉vs机械哥斯拉 (1993)', '哥斯拉vs王者基多拉 (1991)',
    '哥斯拉（2000)', '哥斯拉之终极战役 (2004)',
    '哥斯拉×摩斯拉×机械哥斯拉 (2003)', '哥斯拉再战机械哥斯拉 (2002)',
    '哥斯拉大战超翔龙 (2000)', '致命录像带3',
    '月光光心慌慌12：杀戮', '月光光心慌慌7', '月光光心慌慌10/新万圣节2',
    '海王(Aquaman, 2018)', '海王2:失落的王国(Aquaman and the Lost Kingdom, 2023)',
    '电锯惊魂10 (Saw X,2023)', '电锯惊魂(Saw,2004)', '月光光心慌慌9/索命万圣节',
]

# For each problem title, find matching cover files
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
        if not title:
            continue
        # Check if this is one of the problem cards
        matched = False
        for t in problem_titles:
            if title == t or (len(title) > 3 and title in t) or (len(t) > 3 and t in title):
                matched = True
                break
        if not matched:
            continue
        
        cover_raw = str(vals[1] or '').strip()
        if cover_raw and cover_raw != 'None':
            continue  # Skip cards that already have a path
        
        # Find best match in 缺失封面
        best_match = None
        for cover_name, cover_path in sorted(all_covers.items()):
            # Try various matching strategies
            t_clean = title.replace('【系列合集】','').replace('【系列电影合集】','').replace('【全系列合集】','').strip()
            # Direct match
            if cover_name == title or cover_name == t_clean:
                best_match = cover_path
                break
            # Contains match (check if cover name contains key parts of title)
            if len(title) >= 4:
                title_key = title[:8]
                if title_key in cover_name or cover_name in title:
                    best_match = cover_path
            
        if best_match:
            print(f'{title}')
            print(f'  -> {best_match}')
        else:
            # Try partial match
            print(f'{title}')
            # Find any remotely related cover
            keywords = title.replace('(','').replace(')','').replace('/',' ').replace('：',' ').replace('：',' ').split()
            for kw in keywords:
                if len(kw) < 2: continue
                for cn, cp in sorted(all_covers.items()):
                    if kw in cn:
                        print(f'  partial match: {cn} -> {cp}')
                        break

wb.close()
