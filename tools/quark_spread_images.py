#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Copy promo images into every second-level folder under a Quark folder.

This tool intentionally uses Quark's file/copy API for the fan-out step. Upload
the two source images once into the top folder, then copy those two cloud files
into each child folder.
"""

import argparse
import hashlib
import mimetypes
import os
import sys
import time
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import requests
except ImportError as exc:
    raise SystemExit("pip install requests") from exc


BASE = "https://drive-pc.quark.cn/1/clouddrive"
DEFAULT_IMAGE_DIR = r"F:\1、自媒体\3、网站\影视\宣传图片"
DEFAULT_TARGET_PATH = "电视剧"


class QuarkClient:
    def __init__(self, cookie):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "origin": "https://pan.quark.cn",
                "referer": "https://pan.quark.cn/",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "cookie": cookie,
            }
        )

    @staticmethod
    def _params(extra=None):
        params = {"pr": "ucpro", "fr": "pc", "__t": int(time.time() * 1000)}
        if extra:
            params.update(extra)
        return params

    def get(self, path, params=None):
        response = self.session.get(
            f"{BASE}{path}", params=self._params(params), timeout=30
        )
        response.raise_for_status()
        data = response.json()
        if data.get("code") not in (0, None):
            raise RuntimeError(f"GET {path} failed: {data.get('message')} code={data.get('code')}")
        return data

    def post(self, path, body):
        response = self.session.post(
            f"{BASE}{path}", params=self._params(), json=body, timeout=30
        )
        response.raise_for_status()
        data = response.json()
        if data.get("code") != 0:
            raise RuntimeError(f"POST {path} failed: {data.get('message')} code={data.get('code')}")
        return data

    def list_dir(self, pdir_fid, page=1, size=200):
        data = self.get(
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

    def list_all(self, pdir_fid):
        items = []
        page = 1
        while True:
            batch = self.list_dir(pdir_fid, page=page)
            items.extend(batch)
            if len(batch) < 200:
                break
            page += 1
            time.sleep(0.2)
        return items

    def find_folder(self, path):
        fid = "0"
        name = "root"
        for part in [p.strip() for p in path.split("/") if p.strip()]:
            folders = [item for item in self.list_all(fid) if item.get("dir")]
            found = next((item for item in folders if item.get("file_name") == part), None)
            if found is None:
                found = next((item for item in folders if part in item.get("file_name", "")), None)
            if found is None:
                raise SystemExit(f"Folder '{part}' not found under '{name}'")
            fid = found["fid"]
            name = found["file_name"]
        return fid, name

    def wait_task(self, task_id):
        for retry in range(60):
            data = self.get("/task", {"task_id": task_id, "retry_index": retry})
            status = data.get("data", {}).get("status")
            if status == 2:
                return True
            if status in (3, 4):
                raise RuntimeError(f"Task failed: {task_id} status={status}")
            time.sleep(0.5)
        raise RuntimeError(f"Task timeout: {task_id}")

    def copy_file(self, file_fid, dest_fid):
        data = self.post("/file/copy", {"filelist": [file_fid], "to_pdir_fid": dest_fid})
        task_id = data.get("data", {}).get("task_id")
        if task_id:
            self.wait_task(task_id)
        return data

    def upload_file(self, file_path, dest_fid):
        path = Path(file_path)
        stat = path.stat()
        sha1 = hashlib.sha1()
        md5 = hashlib.md5()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                sha1.update(chunk)
                md5.update(chunk)

        body = {
            "file_name": path.name,
            "pdir_fid": dest_fid,
            "size": stat.st_size,
            "format_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            "l_created_at": int(stat.st_ctime * 1000),
            "l_updated_at": int(stat.st_mtime * 1000),
            "source": "web",
            "upload_type": 1,
            "ccp_hash_update": True,
            "parallel_upload": True,
            "sha1": sha1.hexdigest(),
            "md5": md5.hexdigest(),
        }
        data = self.post("/file/upload/pre", body)
        info = data.get("data", {})
        if info.get("finish"):
            return info

        upload_url = info.get("upload_url") or info.get("uploadUrl")
        upload_id = info.get("upload_id") or info.get("uploadId")
        obj_key = info.get("obj_key") or info.get("objKey")
        auth_info = info.get("auth_info") or info.get("authInfo") or {}
        if not upload_url:
            raise RuntimeError(f"pre_upload returned no upload_url: {info}")

        if isinstance(auth_info, str):
            try:
                import json

                auth_info = json.loads(auth_info)
            except Exception:
                auth_info = {}
        if isinstance(auth_info, dict) and (auth_info.get("policy") or auth_info.get("signature")):
            form = {key: value for key, value in auth_info.items() if value is not None}
            form.setdefault("key", obj_key)
            if info.get("callback"):
                form.setdefault("callback", info.get("callback"))
            with path.open("rb") as fh:
                post = self.session.post(
                    upload_url,
                    data=form,
                    files={"file": (path.name, fh, mimetypes.guess_type(path.name)[0] or "application/octet-stream")},
                    timeout=120,
                )
            post.raise_for_status()
        else:
            headers = {}
            if isinstance(auth_info, dict):
                headers.update(auth_info.get("headers") or {})
            with path.open("rb") as fh:
                put = self.session.put(upload_url, data=fh, headers=headers, timeout=120)
            put.raise_for_status()

        finish_body = {
            "obj_key": obj_key,
            "file_name": path.name,
            "pdir_fid": dest_fid,
            "size": stat.st_size,
            "upload_id": upload_id,
        }
        finish = self.post("/file/upload/finish", finish_body)
        task_id = finish.get("data", {}).get("task_id")
        if task_id:
            self.wait_task(task_id)
        return finish.get("data", {})


def local_images(image_dir):
    root = Path(image_dir)
    if not root.exists():
        raise SystemExit(f"Local image folder not found: {image_dir}")
    paths = [p for p in root.iterdir() if p.is_file()]
    if not paths:
        raise SystemExit(f"No files found in local image folder: {image_dir}")
    return paths


def find_source_files(items, required_names):
    by_name = {item.get("file_name"): item for item in items if not item.get("dir")}
    missing = [name for name in required_names if name not in by_name]
    if missing:
        msg = "\n".join(f"  - {name}" for name in missing)
        raise SystemExit(
            "Source image files are not in the target top folder yet. "
            "Upload these two files into that folder first, then rerun:\n" + msg
        )
    return [by_name[name] for name in required_names]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-path", default=DEFAULT_TARGET_PATH, help="Quark folder path from root, default: 电视剧")
    parser.add_argument("--target-fid", help="Use a folder fid instead of --target-path")
    parser.add_argument("--image-dir", default=DEFAULT_IMAGE_DIR, help="Local folder used only to read required image file names")
    parser.add_argument("--upload-root", action="store_true", help="Upload missing local image files into the target top folder first")
    parser.add_argument("--debug-upload", action="store_true", help="Print upload response keys for troubleshooting")
    parser.add_argument("--execute", action="store_true", help="Actually copy files; default is dry-run")
    parser.add_argument("--limit", type=int, default=0, help="Process only the first N second-level folders")
    args = parser.parse_args()

    cookie = os.environ.get("QUARK_COOKIE")
    if not cookie:
        raise SystemExit("Set QUARK_COOKIE env var first")

    image_paths = local_images(args.image_dir)
    required_names = [path.name for path in image_paths]
    client = QuarkClient(cookie)

    if args.target_fid:
        target_fid, target_name = args.target_fid, args.target_fid
    else:
        target_fid, target_name = client.find_folder(args.target_path)

    top_items = client.list_all(target_fid)
    if args.upload_root:
        top_names = {item.get("file_name") for item in top_items if not item.get("dir")}
        for path in image_paths:
            if path.name in top_names:
                print(f"Root exists: {path.name}")
                continue
            if not args.execute:
                print(f"Root upload dry-run: {path.name}")
                continue
            print(f"Root upload: {path.name}")
            result = client.upload_file(path, target_fid)
            if args.debug_upload:
                print(f"  upload result keys: {sorted(result.keys()) if isinstance(result, dict) else type(result)}")
                if isinstance(result, dict):
                    for key in ("fid", "task_id", "status", "finish", "file_name"):
                        if key in result:
                            print(f"  {key}: {result[key]}")
            time.sleep(0.5)
        top_items = client.list_all(target_fid)
    child_folders = [item for item in top_items if item.get("dir")]
    if args.limit:
        child_folders = child_folders[: args.limit]
    source_files = find_source_files(top_items, required_names)

    print(f"Target: {target_name} ({target_fid})")
    print(f"Second-level folders: {len(child_folders)}")
    print(f"Images: {len(source_files)}")
    for item in source_files:
        print(f"  - {item['file_name']}")
    print("Mode: execute" if args.execute else "Mode: dry-run")
    print()

    copied = 0
    skipped = 0
    failed = 0
    for folder in child_folders:
        dest_items = client.list_all(folder["fid"])
        existing_names = {item.get("file_name") for item in dest_items if not item.get("dir")}
        print(f"[{folder['file_name']}]")
        for source in source_files:
            name = source["file_name"]
            if name in existing_names:
                print(f"  = {name} (exists)")
                skipped += 1
                continue
            if not args.execute:
                print(f"  + {name} (dry-run)")
                copied += 1
                continue
            try:
                client.copy_file(source["fid"], folder["fid"])
                print(f"  + {name}")
                copied += 1
                time.sleep(0.3)
            except Exception as exc:
                print(f"  ! {name}: {exc}")
                failed += 1

    print()
    print(f"Done. planned/copied={copied}, skipped={skipped}, failed={failed}")
    if not args.execute:
        print("Dry-run only. Add --execute to copy files.")


if __name__ == "__main__":
    main()
