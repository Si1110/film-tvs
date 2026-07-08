#!/usr/bin/env python3
"""Check duplicate cards in HTML by examining actual structure"""
import re
from collections import Counter

with open('sections/section-01.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the actual card structure - look at a sample
idx = content.find('card-title')
if idx > 0:
    print('Sample card area:')
    print(content[idx-100:idx+300])
    print('---')

# Extract all card titles
titles = re.findall(r'<h3 class="card-title[^"]*"[^>]*>\s*(.*?)\s*</h3>', content)
print(f'\nTotal cards in HTML: {len(titles)}')

counter = Counter(titles)
dups = {t: c for t, c in counter.items() if c > 1}
print(f'Duplicate titles: {len(dups)}')

sorted_dups = sorted(dups.items(), key=lambda x: -x[1])
print('\nTop 30 duplicates:')
for title, count in sorted_dups[:30]:
    print(f'  [{count}x] {title}')
