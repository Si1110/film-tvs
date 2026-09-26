"""
Scan all quark dir HTML files for garbled names.
Usage: python py/scan_all_garbled.py
Output: summary report, detailed results saved to res/garbled_scan_report.json
"""
import sys, os, json, re, html as html_mod
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.path.dirname(os.path.dirname(__file__))
DIRS_DIR = os.path.join(BASE, 'res', 'dirs')
REPORT_PATH = os.path.join(BASE, 'res', 'garbled_scan_report.json')
JSON_PATH = os.path.join(BASE, 'res', 'quark_name_map.json')

# Pattern: Chinese[-]letter[-]Chinese or Chinese+letter or letter+Chinese
garbled_re = re.compile(r'[\u4e00-\u9fff]-?[A-Z]-?[\u4e00-\u9fff]')

# Pattern: any uppercase letter surrounded by Chinese context
single_letter_re = re.compile(r'[\u4e00-\u9fff]-?([A-Z])-?[\u4e00-\u9fff]')

# Also check for letters in filenames that seem out of place
# (not file extensions like .mkv, not standalone like 4K, 1080P, etc)
solo_letter_re = re.compile(r'(?<![\w.])[A-Z](?![\w.])')

def extract_dir_entries(filepath):
    """Extract file/dir names from a dir HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = []
    # Find all list items - look for the pattern in the HTML
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        # Look for lines with file/dir names containing Chinese
        if any('\u4e00' <= c <= '\u9fff' for c in stripped):
            # Extract the display name from HTML tags
            # Names appear as links or plain text after bullet markers
            # Remove HTML tags
            text = html_mod.unescape(re.sub(r'<[^>]+>', '', stripped)).strip()
            if text and len(text) > 2 and not text.startswith('<'):
                entries.append(text)
    return entries

def has_garbled(name):
    """Check if a name has garbled patterns (Chinese + Latin letter + Chinese)"""
    # Skip file extensions
    name_no_ext = name.rsplit('.', 1)[0] if '.' in name else name
    return bool(garbled_re.search(name_no_ext))

# Load existing mappings
mapped_ids = set()
if os.path.exists(JSON_PATH):
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    mapped_ids = set(data.keys())

# Scan all dir files
results = {}
all_garbled = []
total_dirs = 0
total_entries = 0
total_garbled = 0

for fname in sorted(os.listdir(DIRS_DIR)):
    if not fname.startswith('quark_') or not fname.endswith('.html'):
        continue
    
    total_dirs += 1
    pwd_id = fname.replace('quark_', '').replace('.html', '')
    filepath = os.path.join(DIRS_DIR, fname)
    
    entries = extract_dir_entries(filepath)
    total_entries += len(entries)
    
    garbled_entries = []
    for name in entries:
        if has_garbled(name):
            garbled_entries.append(name)
            all_garbled.append({'pwd_id': pwd_id, 'name': name})
    
    if garbled_entries:
        has_mapping = pwd_id in mapped_ids
        total_garbled += len(garbled_entries)
        results[pwd_id] = {
            'total': len(entries),
            'garbled': len(garbled_entries),
            'has_mapping': has_mapping,
            'entries': garbled_entries[:20]  # Limit to 20 per file
        }

# Save report
report = {
    'total_dirs': total_dirs,
    'total_entries': total_entries,
    'total_garbled': total_garbled,
    'dirs_affected': len(results),
    'details': results,
    'all_garbled': all_garbled
}

with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f'Scanned {total_dirs} dir files')
print(f'Total entries: {total_entries}')
print(f'Garbled entries: {total_garbled}')
print(f'Affected dirs: {len(results)}')
print(f'\nAffected pwd_ids:')
for pwd_id, info in sorted(results.items(), key=lambda x: -x[1]['garbled']):
    status = '✅' if info['has_mapping'] else '❌'
    print(f'  {status} {pwd_id}: {info["garbled"]:>3}/{info["total"]:>3} entries garbled')
print(f'\nFull report: res/garbled_scan_report.json')
