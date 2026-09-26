#!/usr/bin/env python3
"""Check specific cover files."""
import os

checks = [
    ('res/covers/阿凡达火与烬/阿凡达.webp', '阿凡达:火与烬'),
    ('res/movie-covers/宇宙追缉令.webp', '宇宙追缉令'),
    ('res/movie-covers/月光光心慌慌.webp', '月光光心慌慌'),
    ('res/movie-covers/致命录像带.webp', '致命录像带'),
    ('res/movie-covers/功夫.webp', '功夫'),
    ('res/film/合集封面/阿凡达【系列合集】.webp', '阿凡达【系列合集】'),
]
for path, title in checks:
    exists = os.path.exists(path)
    status = 'OK' if exists else 'MISS'
    print(f'[{status}] {path}')
    if not exists:
        base = os.path.splitext(path)[0]
        dirname = os.path.dirname(path)
        basename = os.path.basename(base)
        if os.path.isdir(dirname):
            for f in os.listdir(dirname):
                if basename in f:
                    print(f'    Found similar: {os.path.join(dirname, f)}')
        print(f'    Dir exists: {os.path.isdir(dirname)}')
        # Try .jpg extension
        jpg_path = base + '.jpg'
        if os.path.exists(jpg_path):
            print(f'    Found as .jpg: {jpg_path}')
