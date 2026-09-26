import re


def is_heji(title):
    """Detect if title is a 合集 (contains CJK brackets)"""
    return '\u3010' in title or '\u3014' in title or '\u3018' in title


def extract_theme(title):
    """Extract theme prefix: strip brackets, year+English in parens, season, colon suffix,
    trailing numbers/English/series flags, special suffixes."""
    t = re.sub(r'[【\[（\(][^】\]）\)]*[】\]）\)]', '', title)
    t = re.sub(r'\s*[（(].*?\d{4}[）)].*', '', t)
    t = re.sub(r'\s*第[\d一二三四五六七八九十两]+[季部集]', '', t)
    t = re.sub(r'\s*(?:[SＦ]\d+|Season\s*\d+)', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s*[：:].*', '', t)
    t = re.sub(r'([\u4e00-\u9fff])\d+$', r'\1', t)
    t = re.sub(r'系列$', '', t)
    t = re.sub(r'(\D)\d+$', r'\1', t)
    t = re.sub(r'([\u4e00-\u9fff])\s*\d*\s*[A-Za-z].*$', r'\1', t)
    t = re.sub(r'(?:\s+[\u4e00-\u9fff]{1,15})?(?:特别篇|番外篇|电影版|剧场版|SP|特辑)\s*$', '', t)
    t = re.sub(r'\s*\d{4}\s*\S*$', '', t)
    t = re.sub(r'-[A-Za-z]+版$', '', t)
    t = t.strip()
    ALIASES = {
        '齐天大圣孙悟空': '西游记',
        '天地争霸美猴王': '西游记',
        '西游记续集': '西游记',
        '世界奇妙物语': '世奇',
    }
    return ALIASES.get(t, t)
