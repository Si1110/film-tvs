# -*- coding: utf-8 -*-
import sys, re, os
sys.stdout.reconfigure(encoding='utf-8')

html_path = os.path.join(os.path.dirname(__file__), '..', 'sections', 'section-03.html')
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

titles = re.findall(r'data-title="([^"]+)"', content)
print(f'Total cards with data-title: {len(titles)}')

new_entries = ['命运石之门', '虫师', '反叛的鲁路修', '灵能百分百', '浪客剑心', '石纪元',
               '混沌武士', '一人之下', '鬼灭之刃', '怪物', '攻壳机动队', '紫罗兰永恒花园',
               '间谍过家家', '鬼神童子', '无敌破坏王', '钟楼怪人', '精灵旅社', '功夫熊猫',
               '幽游白书']
for ne in new_entries:
    found = any(ne in t for t in titles)
    status = "OK" if found else "MISSING"
    print(f'  {ne}: {status}')

# Check how many of the 35 new resources appear
source_titles = [
    '命运石之门【系列合集】', '虫师【2季合集】', '反叛的鲁路修【系列合集】',
    '灵能百分百【系列合集】', '浪客剑心【系列合集】', '石纪元【系列合集】',
    '混沌武士', '一人之下【系列合集】', '鬼灭之刃【系列合集】', '怪物 MONSTER',
    '攻壳机动队【系列合集】', '紫罗兰永恒花园【系列合集】', '间谍过家家【系列合集】',
    '鬼神童子', '无敌破坏王【2季合集】', '无敌破坏王', '无敌破坏王2：大闹互联网',
    '钟楼怪人【2季合集】', '钟楼怪人', '钟楼怪人2：老实钟的秘密',
    '精灵旅社【4部合集】', '精灵旅社', '精灵旅社2', '精灵旅社3：疯狂假期',
    '精灵旅社4：变身大冒险', '功夫熊猫【4部合集】', '功夫熊猫', '功夫熊猫2',
    '功夫熊猫3', '功夫熊猫4', '幽游白书【系列合集】', '幽游白书【TV版】',
    '幽游白书：冥界死斗篇·炎之绊', '幽游白书【真人版】', '幽游白书SP：夜叉的阴谋'
]

found_count = 0
missing_list = []
for st in source_titles:
    if st in titles:
        found_count += 1
    else:
        missing_list.append(st)

print(f'\nFound: {found_count}/{len(source_titles)}')
if missing_list:
    print('Missing:')
    for m in missing_list:
        print(f'  - {m}')
