#!/usr/bin/env python3
"""Check which cards have empty cover path vs valid path, and find potential covers."""
import os, openpyxl

xlsx = 'res/data_new.xlsx'
wb = openpyxl.load_workbook(xlsx, data_only=True)

# The user's list
titles = [
    '王牌特工【系列合集】',
    '德州电锯杀人狂 (2003)',
    '德州电锯杀人狂前传 (2006)',
    '007之金刚钻 Diamonds Are Forever (1971)',
    '阿凡达',
    '阿凡达：水之道',
    '女高怪谈 1：死亡教室', '女高怪谈 2：交换日记', '女高怪谈 3：狐狸阶梯',
    '女高怪谈 4：声音', '女高怪谈 5：结伴自杀',
    '芝士火腿 / 咖喱辣椒3', '最佳拍档3：女皇密令',
    '執法先鋒(不死版結局)', '张保仔/怒海侠盗 (1994)', '哗鬼住正隔篱/有鬼住在隔壁',
    '大灵通', '俠盜高飛', '龙潭虎穴/致命摇篮', '宇宙追缉令/救世主',
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
    '电锯惊魂10 (Saw X,2023)', '电锯惊魂(Saw,2004)',
    '月光光心慌慌9/索命万圣节',
]

# Collect movie-covers list for matching
movie_covers = {}
if os.path.isdir('res/movie-covers/'):
    for f in os.listdir('res/movie-covers/'):
        name_no_ext = os.path.splitext(f)[0]
        movie_covers[name_no_ext] = f

print('=== Cards with EMPTY cover path (showing placeholder) ===')
print('These need cover images assigned.\n')

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
        # Check if this title matches any user-provided title
        matched = False
        for t in titles:
            if title == t or title.startswith(t) or t.startswith(title):
                matched = True
                break
        if not matched:
            continue
        
        cover_raw = str(vals[1] or '').strip()
        cover_raw = cover_raw.replace('\\', '/')
        
        if not cover_raw or cover_raw == 'None':
            # Empty path - find potential covers
            print(f'[EMPTY] {title}')
            # Look in movie-covers
            for mc_name, mc_file in sorted(movie_covers.items()):
                if any(kw in mc_name for kw in title.split() if len(kw) > 1):
                    if mc_name != title:
                        print(f'    Potential match: res/movie-covers/{mc_file}')
            # Look in series dirs
            covers_dir = 'res/covers'
            if os.path.isdir(covers_dir):
                for root, dirs, files in os.walk(covers_dir):
                    for f in files:
                        f_noext = os.path.splitext(f)[0]
                        if title[:4] in f_noext or any(kw in f_noext for kw in title[:4].split()):
                            print(f'    Found in covers: {os.path.join(root, f)}')
        else:
            # Has a path - check if file exists
            if cover_raw.startswith('../res/'):
                file_path = cover_raw.replace('../res/', 'res/')
            else:
                file_path = f'res/covers/{cover_raw}'
            exists = os.path.exists(file_path)
            print(f'[{"OK" if exists else "MISS"}] {title} -> {cover_raw}')

wb.close()
