# FilmTVs Section Page Modernization Skill

## Overview
Standardized workflow for adding/editing FilmTVs section pages. Flat card grid + 3-row filter navigation (region/genre/language). Works for all sections (电视剧/电影/动漫).

## Architecture

### File Map
```
py/theme_utils.py          →  Shared: extract_theme(), is_heji()
py/generate_html.py        →  HTML generator (imports theme_utils)
py/verify_sort.py          →  Pre-deploy sort validation (imports theme_utils)
py/deploy_check.py         →  One-command full deployment check
templates/section-tpl.html →  Page skeleton (grid CSS, filter JS)
templates/card-tpl.html    →  Single card template (genre badges, data attrs)
res/data_new.xlsx          →  Source data
docs/css/style.css         →  Check for CSS conflicts
```

### Data Flow
```
Excel (data_new.xlsx) → generate_html.py → section-{n}.html
  ↑ data columns          ↑ generate_section()    ↑ CSS Grid + filter JS
                          ↑ generate_card_html()
  verify_sort.py ←─── reads Excel + HTML ──→ deploy_check.py (orchestrator)
```

## Sorting System (V2 — Flat Theme‑Based)

Algorithm in `generate_section()`:
```
1. _row_idx = each row's Excel line number
2. extract_theme(title) → strip brackets [xx], year (1994), season/subtitle suffixes
3. Group by theme, each group's sort key = -max(row_idx) (newest theme first)
4. Within group:合集 (has 【】) sort = 0, 子集 sort = 1; secondary sort = title
5. Flatten into card grid
```

### extract_theme() — current version
```python
def extract_theme(title):
    t = re.sub(r'[【\[（\(][^】\]）\)]*[】\]）\)]', '', title)       # strip 【...】, [...], etc.
    t = re.sub(r'\s*[（(]\d{4}[）)].*', '', t)                    # strip (1994...)
    t = re.sub(r'\s*\d+$', '', t)                                 # strip trailing digits
    t = re.sub(r'\s*第[一二三四五六七八九十\d一二两三四五六七八九十]+[季部集]', '', t)  # strip 第X季/部/集
    t = re.sub(r'\s*(?:[SＦ]\d+|Season\s*\d+)', '', t, re.I)    # strip S1, Season 1
    t = re.sub(r'\s*[：:].*', '', t)                              # strip ：xxx suffix
    t = re.sub(r'(?:\s+[\u4e00-\u9fff]{1,15})?(?:特别篇|番外篇|电影版|剧场版|SP|特辑)\s*$', '', t)  # strip subtitle
    return t.strip()
```

### is_heji()
```python
def is_heji(t):
    return '\u3010' in t or '\u3014' in t or '\u3018' in t       # 【 〔 〘
```

## Verification Scripts

### 1. verify_sort.py
Run before every deploy:
```bash
python py/verify_sort.py
```
Checks:
- **合集子集系列一致性**: 合集与子集的`所属系列`必须一致（除非子集不同链接→跨合集合法）
- **同名跨系列**: 同标题出现在多个系列时 warning，但不同链接的合法跨系列标为 info
- **必填字段**: 主标题、所属系列、下载链接完整性
- **孤立主题检测 (NEW)**: 检测 `extract_theme` 是否遗漏归一化（如`9号秘事 万圣节`应归入`9号秘事`）
- **HTML 排序验证 (NEW)**: 读取生成的 section HTML，检查每组合集是否在子集之前

### 2. deploy_check.py (NEW)
One-command pre-deployment gate:
```bash
python py/deploy_check.py
```
Runs in order:
1. `python py/generate_html.py` — HTML generation
2. `python py/verify_sort.py` — sort + theme validation
3. BOM contamination check (each section HTML)
4. CSS Grid layout check (card-grid must use `display: grid`, not `row g-3`)

Exit code 0 = all clear; 1 = has errors.

## Known Traps

### Trap 1: Extract theme leaves orphan subtitles → 合集 after 子集
- **When**: Adding an entry like `9号秘事 万圣节特别篇` — old `extract_theme` stripped only `特别篇`, leaving theme `9号秘事 万圣节` instead of `9号秘事`. The orphan theme has higher row-idx (newer entry), renders FIRST, pushing the合集 behind 子集.
- **How deploy_check catches it**: `verify_sort.py` check 4 (orphan theme) detects singleton themes whose `extract_theme` result matches an existing larger theme. Check 5 (HTML sort order) directly verifies合集 is before子集 in the rendered HTML.
- **Fix (applied)**: `\s*[：:].*` moved before the subtitle strip; subtitle match changed to `(?:\s+[\u4e00-\u9fff]{1,15})?(?:特别篇|...)` to strip the preceding descriptive text along with the marker.
- **Don't touch**: `世奇 1993夏季SP` etc. — these are intentional seasonal SP entries that SHOULD stay as separate themes.
- **To verify locally**: `python py/verify_sort.py` (0 errors), then search HTML for the theme's合集 position.

### Trap 2: Flexbox + display:none → card layout deformation
- **When**: Filtering cards via JS, hidden cards are `display:none`. In Flexbox (`row g-3`), remaining cards are re-laid into new rows but retain the original row height, creating uneven card heights.
- **How deploy_check catches it**: Check 4 confirms `.card-grid` uses `display: grid` not `row g-3` (Flexbox).
- **Fix**: CSS Grid with `grid-template-columns: repeat(3, 1fr)`. Grid's `display:none` does NOT trigger this bug.
```css
.card-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
}
@media (max-width: 991px) { grid-template-columns: repeat(2, 1fr); }
@media (max-width: 576px) { grid-template-columns: 1fr; }
```
- **Also prevent overflow**: Add `.card-grid > .card-wrapper { min-width: 0 }` to prevent wide badge content from expanding `1fr` columns.

### Trap 3: Template BOM contamination
- **When**: Template file (card-tpl.html) saved with UTF-8 BOM. Jinja2 repeats the BOM before every rendered card.
- **How deploy_check catches it**: Check 3 scans all section HTML files for BOM bytes (`\xef\xbb\xbf`).
- **Fix**: `content.replace(b'\xef\xbb\xbf', b'')` in Python, or save template without BOM.
- **Verify manually**: `python -c "with open('sections/section-01.html','rb') as f: c=f.read(); print('bom:', c[:3]==b'\\xef\\xbb\\xbf', 'count:', c.count(b'\\xef\\xbb\\xbf'))"`

## Deployment Checklist

```bash
# 1. Generate HTML (required before deploy)
python py/generate_html.py

# 2. Run full validation gate (NEW — catches all known traps)
python py/deploy_check.py

# 3. Only if deploy_check returns 0:
git add .
git commit -m "deploy: update sections"
git push origin res
```

## Workflow — Adding New Data

1. **Update Excel**: Replace `res/data_new.xlsx` with new data
2. **Run deploy_check**: `python py/deploy_check.py`
3. **If errors**:
   - Orphan themes → fix `extract_theme` in `theme_utils.py`
   - Sort order → check `generate_section()` grouping
   - BOM → fix template file encoding
   - Grid/Flexbox → fix section-tpl.html CSS

## Key Contact Points in Code

| What | Where |
|------|-------|
| Theme extraction (season/subtitle stripping) | `py/theme_utils.py:extract_theme()` |
| Sort grouping (合集 first) | `py/generate_html.py:generate_section()` |
| Card HTML structure | `templates/card-tpl.html` |
| Grid + filter JS | `templates/section-tpl.html` |
| Pre-deploy validation | `py/deploy_check.py` |
| Sort/orphan validation | `py/verify_sort.py` |
