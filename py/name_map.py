"""
name_map.py — 夸克脱敏名称映射模块

功能:
  维护一个基于 fid 的名称映射表（fid 是 Quark 文件唯一ID，重命名后不变）
  映射表保存到 res/quark_name_map.json

结构:
  {
    "pwd_id_hash": {
      "title": "资源标题(供参考)",
      "fid_xxx": "正确显示名称",
      "fid_yyy": "另一个文件.mp4"
    }
  }

用法:
  from py.name_map import NameMapper
  nm = NameMapper()
  nm.set("pwd_id", "fid_123", "正确名称")
  nm.apply(pwd_id, entries) -> 替换entries中的name
"""
import os, json, re

MAP_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'res', 'quark_name_map.json')

class NameMapper:
    def __init__(self):
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(MAP_FILE):
            try:
                with open(MAP_FILE, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                self.data = {}

    def save(self):
        os.makedirs(os.path.dirname(MAP_FILE), exist_ok=True)
        with open(MAP_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def _key(self, pwd_id):
        return pwd_id

    def set_title(self, pwd_id, title):
        k = self._key(pwd_id)
        self.data.setdefault(k, {})
        self.data[k]['_title'] = title

    def get_title(self, pwd_id):
        k = self._key(pwd_id)
        return self.data.get(k, {}).get('_title', '')

    def set(self, pwd_id, fid, display_name):
        """设置单个 fid 的映射"""
        k = self._key(pwd_id)
        self.data.setdefault(k, {})
        self.data[k][fid] = display_name

    def get(self, pwd_id, fid):
        """获取单个 fid 的映射"""
        k = self._key(pwd_id)
        return self.data.get(k, {}).get(fid)

    def get_all(self, pwd_id):
        """获取整个 pwd_id 的映射（不含 _title）"""
        k = self._key(pwd_id)
        d = self.data.get(k, {})
        return {k2: v2 for k2, v2 in d.items() if not k2.startswith('_')}

    def remove(self, pwd_id, fid):
        k = self._key(pwd_id)
        if k in self.data and fid in self.data[k]:
            del self.data[k][fid]
            self.save()

    def remove_pwd(self, pwd_id):
        k = self._key(pwd_id)
        self.data.pop(k, None)
        self.save()

    def list_pwd_ids(self):
        """列出所有有映射的 pwd_id"""
        return [k for k in self.data if not k.startswith('_')]

    def apply(self, pwd_id, entries):
        """
        对 entries 列表应用映射，就地替换 name
        entries 格式: [{'fid': '...', 'name': '...', ...}, ...]
        返回替换的数量
        """
        mapping = self.get_all(pwd_id)
        if not mapping:
            return 0
        count = 0
        for e in entries:
            fid = e.get('fid', '')
            if fid in mapping:
                if e['name'] != mapping[fid]:
                    e['name'] = mapping[fid]
                    count += 1
        return count

    def apply_to_html(self, pwd_id, html_content):
        """对已生成的 HTML 内容应用映射（备用方案，按 fid 精确替换）"""
        mapping = self.get_all(pwd_id)
        if not mapping:
            return html_content
        # 不对HTML进行fid替换，fid不在HTML中
        # 这个方法保留供未来使用
        return html_content

    def stats(self, pwd_id=None):
        """统计映射数量"""
        if pwd_id:
            return len(self.get_all(pwd_id))
        total = 0
        for k in self.data:
            if not k.startswith('_'):
                total += len([v for v in self.data[k] if not v.startswith('_')])
        return total
