#!/usr/bin/env python3
"""Recursively rename Quark anime folders with dashed/pinyin Chinese titles."""

import argparse
import os
import re
import sys
import time
from collections import Counter, defaultdict

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import requests
except ImportError as exc:
    raise SystemExit("pip install requests") from exc

try:
    from pypinyin import Style, pinyin
except ImportError as exc:
    raise SystemExit("pip install pypinyin") from exc


BASE = "https://drive-pc.quark.cn/1/clouddrive"
COOKIE = os.environ.get("QUARK_COOKIE")
if not COOKIE:
    raise SystemExit("Set QUARK_COOKIE env var")

SESSION = requests.Session()
SESSION.headers.update(
    {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://pan.quark.cn",
        "referer": "https://pan.quark.cn/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "cookie": COOKIE,
    }
)


def ts():
    return int(time.time() * 1000)


def params(extra=None):
    value = {"pr": "ucpro", "fr": "pc", "__t": ts()}
    if extra:
        value.update(extra)
    return value


def api_get(path, query=None):
    data = SESSION.get(f"{BASE}{path}", params=params(query), timeout=30).json()
    if data.get("code") != 0:
        raise RuntimeError(f"GET {path} failed: {data.get('message')} code={data.get('code')}")
    return data


def api_post(path, body):
    data = SESSION.post(f"{BASE}{path}", params=params(), json=body, timeout=30).json()
    if data.get("code") != 0:
        raise RuntimeError(f"POST {path} failed: {data.get('message')} code={data.get('code')}")
    return data


def list_dir(pdir_fid, page=1, size=200):
    data = api_get(
        "/file/sort",
        {
            "pdir_fid": pdir_fid,
            "force": 0,
            "_page": page,
            "_size": size,
            "_sort": "file_type:asc,file_name:asc",
        },
    )
    return data.get("data", {}).get("list", [])


def list_all(pdir_fid):
    items = []
    page = 1
    while True:
        batch = list_dir(pdir_fid, page=page)
        items.extend(batch)
        if len(batch) < 200:
            break
        page += 1
        time.sleep(0.2)
    return items


def find_folder(path):
    fid = "0"
    name = "root"
    for part in [p.strip() for p in path.split("/") if p.strip()]:
        folders = [it for it in list_all(fid) if it.get("dir")]
        found = next((it for it in folders if it.get("file_name") == part), None)
        if found is None:
            found = next((it for it in folders if part in it.get("file_name", "")), None)
        if found is None:
            raise SystemExit(f"Folder '{part}' not found under '{name}'")
        fid = found["fid"]
        name = found["file_name"]
    return fid, name


def cjk(ch):
    return "\u4e00" <= ch <= "\u9fff"


def initial(ch):
    value = pinyin(ch, style=Style.FIRST_LETTER)
    if value and value[0] and value[0][0]:
        return value[0][0].upper()
    return ch


# Known non-title Chinese suffixes (appended directly after a title)
# These are checked recursively so that e.g. "内封中文字幕" is handled as
# "内封" + "中文字幕" instead of prefix being re-transformed.
_NON_TITLE_SUFFIXES = sorted([
    '备份字幕', '外挂字幕', '内嵌字幕', '字幕备份',
    '番外之类的', '番外篇', '番外',
    '剧场版', '特别篇', '特别版',
    '收藏版', '修复版', '精选版', '重置版', '高码版',
    '在线观看', '在线观看版',
    '国语版', '粤语版', '日语版', '中文版', '英文版',
    '简日双语', '繁日双语',
    '日文', '中文', '国语', '粤语',
    '合集', '全集', '精选集', '汇编',
    '全彩', '黑白',
    '备份', '字幕',
    '漫画', '原版', '动漫',
    '超清', '高清', '内封', '中文字幕', '字幕组', '简日双语',
    '国粤双语', '国日双语', '系列', '完结', '集全', '双语',
    '简体', '繁体', '完整', '正版', '视频', '音频',
    '补发', '下载', '分享',
], key=len, reverse=True)

# Folders/files whose entire Chinese content is a known non-title term (skip transform)
_NON_TITLE_ENTIRE = {
    '字幕', '备份', '漫画', '动画', '音频', '视频', '原版', '动漫',
    '国语', '日语', '粤语', '中文', '英文', '日文',
    '剧场版', '特别篇', '特别版', '番外篇', '番外',
    '高码版', '重置版', '精选版', '收藏版', '修复版',
    '合集', '全集', '精选集', '汇编',
    '全彩', '黑白',
    '本篇', '完结篇', '完整版',
    '国语版', '粤语版', '日语版', '中文版', '英文版',
    '在线观看', '在线观看版',
    '第一季', '第二季', '第三季', '第四季', '第五季', '第六季',
    '第七季', '第八季', '第九季', '第十季',
    '精选版', '原版', '重置版', '高码版',
    '漫画pdf', '简体内嵌',
    '简日双字', '繁日双字',
    '外挂字幕合集',
    '超清', '高清', '完整', '正版',
    '内封',
    '中文字幕', '字幕组', '简日双语',
    '国粤双语', '国日双语',
    '系列', '完结', '集全',
    '双语',
    '简体', '繁体',
    '补发', '下载', '分享',
}


def transform_chinese_run(run):
    tokens = []
    for index, ch in enumerate(run, start=1):
        tokens.append(initial(ch) if index % 2 == 0 else ch)
    return "-".join(tokens)


def strip_level_one_prefix(name):
    return re.sub(r"^[A-Z]\s+", "", name, count=1)


def _transform_chinese_segment(segment, changed):
    """Transform a contiguous Chinese run, respecting title/non-title boundaries.
    Returns (transformed_string, was_changed)."""
    # Entire segment is known non-title
    if segment in _NON_TITLE_ENTIRE:
        return segment, False
    # Check if segment ends with a known non-title suffix
    for suffix in _NON_TITLE_SUFFIXES:
        if segment.endswith(suffix):
            prefix = segment[: -len(suffix)]
            if prefix:
                # The prefix might itself be a known non-title term or
                # end with a suffix. Recurse to handle concatenated terms.
                trans_prefix, pref_changed = _transform_chinese_segment(prefix, changed)
                return trans_prefix + suffix, pref_changed
            # suffix IS the whole segment → non-title
            return segment, False
    # Pure title → transform all
    return transform_chinese_run(segment), True


def transform_name(name, depth):
    value = strip_level_one_prefix(name) if depth == 1 else name
    out = []
    i = 0
    changed_chinese = False
    while i < len(value):
        if cjk(value[i]):
            start = i
            while i < len(value) and cjk(value[i]):
                i += 1
            segment = value[start:i]
            transformed, changed = _transform_chinese_segment(segment, changed_chinese)
            out.append(transformed)
            if changed:
                changed_chinese = True
            if i < len(value) and value[i].isascii() and value[i].isalnum():
                out.append(" ")
        else:
            out.append(value[i])
            i += 1
    result = "".join(out)
    if changed_chinese:
        result = re.sub(r"\s+", " ", result).strip()
    return result


def collect(root_fid, root_name, file_mode=False):
    stack = [(root_fid, root_name, 0)]
    folders = []
    children_by_parent = defaultdict(list)
    scanned_dirs = 0
    while stack:
        parent_fid, parent_path, parent_depth = stack.pop()
        scanned_dirs += 1
        if scanned_dirs == 1 or scanned_dirs % 50 == 0:
            label = "files" if file_mode else "folders"
            print(f"Scanning: opened={scanned_dirs} found={len(folders)}", flush=True)
        items = list_all(parent_fid)
        children = items if file_mode else [it for it in items if it.get("dir")]
        for child in children:
            depth = parent_depth + 1
            is_dir = child.get("dir", False)
            record = {
                "fid": child["fid"],
                "parent_fid": parent_fid,
                "name": child["file_name"],
                "depth": depth,
                "path": f"{parent_path}/{child['file_name']}",
                "dir": is_dir,
            }
            folders.append(record)
            children_by_parent[parent_fid].append(record)
            if is_dir:
                stack.append((child["fid"], record["path"], depth))
        time.sleep(0.05)
    return folders, children_by_parent


def plan_renames(folders, children_by_parent):
    planned = []
    for record in folders:
        fixed = fix_over_transformed(record["name"])
        new_name = strip_copyright(transform_name(fixed, record["depth"]))
        if new_name != record["name"]:
            planned.append({**record, "new_name": new_name})

    conflicts = []
    planned_by_parent = defaultdict(dict)
    for item in planned:
        planned_by_parent[item["parent_fid"]][item["fid"]] = item["new_name"]

    for parent_fid, children in children_by_parent.items():
        final_names = []
        for child in children:
            final_names.append(planned_by_parent[parent_fid].get(child["fid"], child["name"]))
        for name, count in Counter(final_names).items():
            if count > 1:
                conflicts.append((parent_fid, name, count))

    return planned, conflicts


def rename_item(fid, new_name):
    api_post("/file/rename", {"fid": fid, "file_name": new_name})


# Pre-compute fix map: for each known non-title term, compute what
# transform_chinese_run produces, then map back to the raw term.
# If multiple terms map to the same transformed pattern (collision),
# skip all of them to avoid ambiguity (e.g. 第四季/第十季 → 第-S-季).
_FIX_MAP = {}
_FIX_COLLISIONS = set()
for _term in sorted(set(_NON_TITLE_SUFFIXES) | _NON_TITLE_ENTIRE, key=len, reverse=True):
    _trans = transform_chinese_run(_term)
    if _trans != _term:
        if _trans in _FIX_MAP or _trans in _FIX_COLLISIONS:
            _FIX_COLLISIONS.add(_trans)
            _FIX_MAP.pop(_trans, None)
        else:
            _FIX_MAP[_trans] = _term


# Transformed patterns that are known false positives (should NOT be fixed),
# because a shorter transformed term happens to match a different original word.
# E.g. "字-M" can come from "字幕" (non-title) or "字母歌" (title).
_FALSE_POSITIVES = {
    "字-M-歌",  # "字母歌" (alphabet song) NOT "字幕歌"
}

# Platform/copyright terms to strip from names (remove entirely, not just preserve)
_COPYRIGHT_TERMS = {"优酷", "爱奇艺", "腾讯"}


def strip_copyright(name):
    """Remove copyright terms and clean up leftover dashes/spaces.
    Returns original name if stripping would produce empty string."""
    original = name
    for term in _COPYRIGHT_TERMS:
        # Remove with leading dash (e.g. "-优酷", "-优酷-" at end)
        # Try dash-prefixed versions first (for transformed names)
        patterns = [
            f"-{term}",        # -优酷 (mid or end)
            f"{term}-",        # 优酷- (start or mid)
            f"-{term}-",       # -优酷- (mid)
            term,              # bare term
        ]
        for pat in patterns:
            while pat in name:
                name = name.replace(pat, "")
    # Clean up: remove double dashes, trailing/leading dashes/spaces
    while "--" in name:
        name = name.replace("--", "-")
    name = name.strip("- ")
    return name if name else original


def fix_over_transformed(name):
    """Undo over-transformation of known non-title terms.
    Uses left-to-right greedy matching: for each position, tries the longest
    fix pattern first. After a fixed term, consumes a trailing dash if the
    next character is CJK (the dash was between two transformed terms)."""
    # Protect known false-positive patterns with markers
    markers = {}
    for i, fp in enumerate(sorted(_FALSE_POSITIVES, key=len, reverse=True)):
        if fp in name:
            m = f"\x00FP_MARKER_{i}\x00"
            markers[m] = fp
            name = name.replace(fp, m)

    patterns = sorted(_FIX_MAP, key=len, reverse=True)
    result = []
    i = 0
    while i < len(name):
        matched = False
        for pat in patterns:
            if name.startswith(pat, i):
                result.append(_FIX_MAP[pat])
                i += len(pat)
                # Consume trailing dash if it was between two transformed terms
                if i < len(name) and name[i] == "-" and i + 1 < len(name) and cjk(name[i + 1]):
                    i += 1
                matched = True
                break
        if not matched:
            result.append(name[i])
            i += 1

    final = "".join(result)
    for m, fp in markers.items():
        final = final.replace(m, fp)
    return final


def plan_file_renames(files, children_by_parent):
    """Plan renames for video files."""
    VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".m4v", ".mov", ".wmv", ".flv", ".webm", ".ts", ".m2ts"}
    planned = []
    for record in files:
        if record["dir"]:
            continue
        name = record["name"]
        # Separate extension
        dot = name.rfind(".")
        if dot == -1:
            base, ext = name, ""
        else:
            ext = name[dot:].lower()
            if ext not in VIDEO_EXTS:
                continue
            base = name[:dot]
        new_base = strip_copyright(transform_name(fix_over_transformed(base), record["depth"]))
        new_name = new_base + name[dot:]
        if new_name != name:
            planned.append({**record, "new_name": new_name})

    # Conflict check: same parent cannot have duplicate new names
    conflicts = []
    planned_by_parent = defaultdict(dict)
    for item in planned:
        planned_by_parent[item["parent_fid"]][item["fid"]] = item["new_name"]
    for parent_fid, children in children_by_parent.items():
        final_names = []
        for child in children:
            final_names.append(planned_by_parent[parent_fid].get(child["fid"], child["name"]))
        for name, count in Counter(final_names).items():
            if count > 1:
                conflicts.append((parent_fid, name, count))

    return planned, conflicts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--find-path", default="动漫资源")
    parser.add_argument("--fid", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--files", action="store_true", help="Rename video files instead of folders")
    parser.add_argument("--limit", type=int, default=120, help="Max planned changes to print; 0 prints all")
    args = parser.parse_args()

    if args.fid:
        root_fid = args.fid
        root_name = args.find_path or args.fid
    else:
        root_fid, root_name = find_folder(args.find_path)

    print(f"Target: {root_name} (FID: {root_fid})", flush=True)
    items, children_by_parent = collect(root_fid, root_name, file_mode=args.files)

    if args.files:
        planned, conflicts = plan_file_renames(items, children_by_parent)
        label = "Files"
    else:
        planned, conflicts = plan_renames(items, children_by_parent)
        label = "Folders"

    print(f"{label} scanned: {len(items)} | Changes planned: {len(planned)}", flush=True)

    if conflicts:
        print("Conflicts detected; aborting:")
        for parent_fid, name, count in conflicts:
            print(f"  parent={parent_fid} name={name} count={count}", flush=True)
        raise SystemExit(2)

    ordered = sorted(planned, key=lambda it: it["depth"], reverse=True)
    visible = ordered
    if args.dry_run and args.limit:
        visible = ordered[: args.limit]
    for item in visible:
        print(f"  {item['path']} -> {item['new_name']}", end="", flush=True)
        if args.dry_run:
            print("  [dry-run]", flush=True)
            continue
        rename_item(item["fid"], item["new_name"])
        print(flush=True)
        time.sleep(0.05)

    if args.dry_run and args.limit and len(ordered) > args.limit:
        print(f"... {len(ordered) - args.limit} more planned changes not shown", flush=True)


if __name__ == "__main__":
    main()
