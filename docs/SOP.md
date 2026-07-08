# 影视资源上架 SOP

> 适用于：提供影视资源名称和链接后，完成全部上架流程

## 一、基本规则

| 类型 | 所属系列规则 | 分类 Sheet |
|------|-------------|-----------|
| 国产电视剧（含港台） | 归入"国产精品系列" | 电视剧资源 |
| 国产电影 | 归入"华语精选系列" | 电影资源 |
| 欧美/日韩/西班牙/泰等外国电影 | 归入"欧美大片系列"（恐怖片除外） | 电影资源 |
| 恐怖/惊悚类电影（不分国别） | 归入"恐怖惊悚系列" | 电影资源 |
| 动漫资源 | 大IP（如东京食尸鬼、数码暴龙等）自成一系 | 动漫资源 |
| 动漫资源 | 单部或小众作品归入"精选动画系列" | 动漫资源 |

**单视频条目（非系列合集）不写"系列"，所属系列直接写条目本身标题。**

## 二、完整上架流程

### Step 1：确定分类归属

拿到资源名称和链接后，先判断：
1. **类型**：电视剧/电影/动漫
2. **系列归属**：按上述规则确定所属系列
3. **语言**：根据视频实际语言填写（不可猜测）
   - 英语：绝命毒师/哈利波特等英美作品
   - 日语：动漫/日剧/日本电影
   - 汉语普通话：国产剧/国产电影
   - 粤语/国语：港剧双语音轨
   - 韩语：韩剧/韩国电影
   - 泰语/西班牙语/德语等按实际填写
4. **字幕**：一般填"中文字幕"
5. **网盘名称**：夸克网盘 / 百度网盘

### Step 2：确认语言信息

**语言是最容易出错的地方，必须根据视频原始语言确认，不可凭猜测或默认填写。**

操作流程：
1. **已知知名作品**：直接凭知识填写
   - 《绝命毒师》《哈利波特》→ 英语
   - 《数码暴龙》《鬼灭之刃》→ 日语
   - 《甄嬛传》《琅琊榜》→ 汉语普通话
   - 《星空下的仁医》→ 粤语/国语
2. **不确定或新作品**：联网搜索确认
   - 搜索方式：`{作品名} 语言` 或 `{作品名} 配音语言`
   - 西班牙语电影（如《谍杀风暴》）→ 西班牙语
   - 泰语电影（如《鬼女佣》《泥娃娃》）→ 泰语
   - 德语电影（如《茜茜公主》）→ 德语
   - 潮汕话/闽南语作品 → 按实际方言填写，如"潮汕话/国语"
3. **查看网盘目录文件名线索**：菜单文件名中常含语言信息
4. **有中文字幕的作品**：语言字段填原声语言，字幕字段填"中文字幕"，二者独立

常见对照表：
| 作品来源 | 语言 | 实例 |
|---------|------|------|
| 英美/加拿大/澳洲 | 英语 | 绝命毒师、老友记、斯巴达克斯、识骨寻踪 |
| 日本 | 日语 | 动漫、日剧、日本电影 |
| 中国内地 | 汉语普通话 | 国产剧、国产电影 |
| 中国香港（原声） | 粤语 | 港剧、周星驰电影粤语版 |
| 港剧双语 | 粤语/国语 | 星空下的仁医、宫 |
| 韩国 | 韩语 | 蓝色生死恋、釜山行、老男孩 |
| 泰国 | 泰语 | 鬼女佣、泥娃娃 |
| 西班牙/墨西哥 | 西班牙语 | 谍杀风暴、天启Z |
| 德国/奥地利 | 德语 | 茜茜公主 |
| 潮汕/闽南地区 | 潮汕话/国语 | 给阿嬷的情书 |

### Step 3：编辑简介（概要）

**每条目必须有简介，不可留空。**

操作流程：
1. **知名经典作品**（豆瓣评分高、广泛认知）→ 凭知识直接编写
   - 格式：20-80字，描述作品类型 + 剧情概要 + 看点
   - 示例：*"经典日本热血动漫，讲述鸣人从吊车尾成长为火影的励志故事。包含疾风传全系列，中文字幕版。"*
2. **2025/2026 新作品**或不确定的作品 → 联网搜索后编写
   - 搜索方式：`{作品名} 剧情 简介`
   - 核实出品年份、主创、剧情概要
   - 不可编造事实
3. **夸克网盘资源**（有 API 目录数据时）→ 自动从目录树提取版本信息
   - 示例：*"收录了1983版、1994版、2003版、2008版、2017版等5个版本的射雕英雄传电视剧大全集。"*
   - 脚本 `listing.py` / `batch_list.py` 会尝试自动生成

编写规范：
- 开头用"收录了"或"经典"或直接描述
- 包含作品类型（热血/悬疑/恐怖/爱情等）
- 末尾加"中文字幕版"或"高清资源下载"
- 一句话描述即为最佳，不超过三句

### Step 4：写入 Excel（`res/data_new.xlsx`）

打开对应 Sheet，新增一行填写字段：

| 字段 | 说明 |
|------|------|
| 所属系列 | 按 Step 1 规则填 |
| 封面图片路径 | `../res/covers/{系列名}/{标题key}.webp` |
| 主标题 | 资源显示名称 |
| 副标题 | 版本信息（如有），如"7个版本大合集" |
| 概要 | 简介文字，按 Step 3 编写 |
| 语言 | 按 Step 2 确认，必须与实际一致 |
| 字幕 | 一般填"中文字幕" |
| 目录路径 | 百度网盘菜单文件名（不含_menu.txt）或夸克目录HTML文件key |
| 网盘名称 | 夸克网盘 / 百度网盘 |
| 下载链接 | 完整分享链接 |
| 解压密码 | 有则填，无则留空 |
| 支持格式 | mp4 / mp4/mkv |
| 卡片页脚 | 如"3个版本 共约30集" |

### Step 5：封面处理

封面存放路径：`res/covers/{所属系列}/{标题key}.webp` 或 `.jpg`

优先顺序：
1. **用户提供**：从 `F:\1、自媒体\3、网站\影视\缺失封面\` 查找是否有同名文件
2. **豆瓣 API**：用 `listing.py` 或 `batch_list.py` 的豆瓣搜索自动下载
3. **百度图片搜索**：手动搜索并保存
4. **Bing图片搜索**：备选

封面文件命名规则：去除特殊字符，用下划线连接，如 `超级宝贝JOJO.jpg`

### Step 6：卡片目录菜单（百度网盘资源）

**此步极为重要。每张卡片上的"目录"按钮点击后弹窗显示目录内容，数据来自 `res/dirs/{key}.html`。Excel 中 `目录路径` 列的值必须对应 `res/dirs/` 下的一个 HTML 文件。**

目录加载机制（`docs/js/dir-modal.js`）：
```
卡片按钮 `data-dir-key="xxx"` → fetch `res/dirs/xxx.html` → 弹窗显示
若 fetch 失败 → 显示"暂无详细目录"
若 xxx 以 http 开头 → 显示"打开网盘"按钮（跳转链接）
```

两种目录数据源：

**方式 A：夸克 API 自动生成**（见 Step 7）

**方式 B：手动创建目录 HTML**（适用于百度网盘资源）

1. 在 `res/dirs/` 下创建 `{key}.html` 文件（key 与 Excel `目录路径` 列的值一致）
2. HTML 格式（支持多级文件夹嵌套，每层缩进 24px）：
```html
<div class="dir-list">
  <div class="dir-section mb-3">
    <h6 style="color:#ffd700;border-bottom:1px solid rgba(255,215,0,0.2);padding-bottom:8px;margin-bottom:12px;">
      <i class="bi bi-folder2-open"></i> 百度网盘目录
    </h6>
    <!-- 一级文件夹 -->
    <div style="margin-left:0px" class="mb-1">
      <div class="d-flex align-items-center mb-1">
        <span style="color:#ffd700;">📁 一级文件夹</span>
        <span class="badge bg-secondary ms-2" style="font-size:0.7rem;">N 项</span>
      </div>
      <!-- 二级内容 -->
      <div style="margin-left:24px" class="mb-1">
        <div class="d-flex align-items-center mb-1">
          <span style="color:#ffd700;">📁 二级文件夹</span>
        </div>
        <!-- 三级文件 -->
        <div style="margin-left:24px;color:#aaa;font-size:0.9rem;" class="mb-1">📄 文件.mp4</div>
      </div>
      <!-- 一级文件 -->
      <div style="margin-left:24px;color:#aaa;font-size:0.9rem;" class="mb-1">📄 文件.mp4</div>
    </div>
  </div>
</div>
```
- 每级缩进使用 `margin-left:{N*24}px`
- 文件夹用 `📁` + `color:#ffd700`
- 文件用 `📄` + `color:#aaa`
3. 也可记录到 `res/baidu-menus/` 目录下作为备份参考（txt 格式，非必需，仅人工查阅用）

**确认目录按钮可用的方法**：运行 `python py/generate_html.py` 后，打开生成的 section HTML，点击卡片目录按钮应能正常弹出目录内容。

### Step 7：夸克网盘目录（仅夸克网盘资源）

1. 用 `listing.py` 或 `batch_list.py` 的夸克 API 自动读取文件夹结构
2. 脚本自动在 `res/dirs/` 下生成 `{系列名}.html` 目录文件（格式与 Step 6 方式 B 相同）
3. Excel 中 `目录路径` 列写入系列名 key（必须与 `res/dirs/` 文件名一致，不含 `.html`）
4. 验证：打开对应 section HTML，点击卡片目录按钮，应弹出夸克文件夹结构

### Step 7a：脱敏名称映射（重要）

**问题**：为防和谐修改了网盘内文件夹/视频名称后，网站目录显示的是脱敏后的错误名称。

**解决方案**：基于 Quark 文件唯一 ID（fid，重命名后不变）维护名称映射表。

**映射文件**：`res/quark_name_map.json`

**工作流程**：

1. **查看当前脱敏名称**（首次或修改网盘文件名后）：
   ```
   python py/name_map_tool.py fetch <夸克分享链接>
   ```
   输出所有文件的 fid 和当前脱敏名。

2. **逐个设定正确名称**：
   ```
   python py/name_map_tool.py map <pwd_id> <fid> <正确名称>
   ```
   例：`python py/name_map_tool.py map 6307cf2189a5 c811fbd0a19247f49c9b96faea69316c 致命弯道系列 1-7`

3. **批量应用映射并重新生成目录 HTML**：
   ```
   python py/name_map_tool.py batch <pwd_id>
   ```
   从夸克重新获取目录 → 应用映射表替换名称 → 生成 `res/dirs/quark_{pwd_id}.html`

4. **查看所有未映射的脱敏名**：
   ```
   python py/name_map_tool.py suggest <pwd_id>
   ```

5. **查看已保存的映射**：
   ```
   python py/name_map_tool.py list
   python py/name_map_tool.py show <pwd_id>
   ```

**自动集成**：`quark_batch_update2.py` 批量生成目录时自动读取 `quark_name_map.json` 并应用映射。只需维护好映射文件，后续每次批量生成都不会再出现脱敏名。

**关键原则**：
- 映射基于 fid（文件内部ID），**改文件名不老映射仍然有效**
- 仅需在**首次**或**修改网盘文件名后**更新映射
- 映射文件是 JSON 格式，可直接编辑

### Step 8a：目录完整性验证

生成目录HTML后，必须运行验证脚本检查所有卡片的目录文件是否存在、名称是否完整：

```
python py/verify_deploy.py
```

脚本检查三项：
1. **夸克资源必须有 col8 目录路径** → Excel `目录路径` 列不能为空
2. **目录文件存在** → `res/dirs/{key}.html` 文件必须存在
3. **目录名称无脱敏残留** → 不会显示谐音/脱敏后的文件名

常见问题：
- 夸克资源缺少 dir_key：需补充 Excel col8 的值（如 `quark_{pwd_id}` 或系列名 key）
- 脱敏残留文件名：需手动修正目录 HTML 文件，替换为正确名称
- 温子仁系列/致命弯道等特殊目录：直接写正确名称，不用夸克 API 原始名

**每次上架后必须运行验证，确认全部通过后才可发布。**

### Step 9a：同系列卡片排序（自动）

`generate_html.py` 已内置排序逻辑：
1. **电视剧区**：按 `res/影视动漫新增（0610）.xlsx` 的原始行顺序排序（按区段分组），合集自动排在子集之前
2. **电影/动漫区**：按标题自然排序
3. **排序参考表必须与 data_new.xlsx 同步更新**，否则排序可能错乱

⚠️ 注意事项：
- 同名条目在不同区段（如"射雕英雄传 (1994)"同时出现在国产精品和港台剧精选）会独立排序
- 如果同系列条目被分到不同所属系列，会导致同一主题散落在不同分组里

只需确保 Excel 中每行 `所属系列` 填写正确，运行生成脚本即可。

### Step 9b：排序预检

```bash
python py/verify_sort.py
```

运行后检查输出：
- **ERROR** → 必须修复后再部署（通常为合集子集系列不一致）
- **WARN** → 建议人工确认（可能为合法跨系列同名条目）
- **INFO** → 正常提示

### Step 10：生成 HTML

运行：
```
python py/generate_html.py
```

这会：
- 读取 `res/data_new.xlsx` 所有数据
- 从 `res/README.md` 加载配置（标题/SEO/热点推荐）
- 生成 `index.html`（含热点推荐卡片）
- 生成 `sections/section-01.html`（电视剧/199张卡片）
- 生成 `sections/section-02.html`（电影/93张卡片，分恐怖惊悚/欧美大片/华语精选，组内按标题自然排序）
- 生成 `sections/section-03.html`（动漫/244张卡片）
- 更新 `docs/js/` 下的 JS 配置文件

### Step 11：热点推荐配置（可选）

编辑 `res/README.md` 中的热点配置：

```python
HOT_ITEMS_TV=灵魂摆渡,神探狄仁杰,识骨寻踪           # 电视剧：填具体剧名
HOT_ITEMS_MOVIE=哪吒之魔童降世,给阿嬷的情书,阿凡达   # 电影：填具体片名
HOT_SERIES_ANIME=数码暴龙系列,魔卡少女樱系列,三大民工漫  # 动漫：填系列名
```

**热点封面**：放在 `res/hot-covers/` 目录下，命名 `{标题}.jpg`（需与 Excel 主标题一致），独立于子页面封面。

### Step 12：提交发布

```bash
git add -A
git commit -m "上架 {资源名}"
git push
```

## 三、使用脚本快捷上架（夸克资源）

### listing.py 交互式上架

```bash
# 交互式选择源表条目
python py/listing.py 上架 --from-source

# 按名称模糊查找
python py/listing.py 上架 --name "射雕英雄传"

# 按源表行号
python py/listing.py 上架 --id 36

# 上架但不 push
python py/listing.py 上架 --name "XXX" --no-push
```

### batch_list.py 批量上架（源表全量处理）

```bash
python py/batch_list.py
```

环境变量：
- `QUARK_COOKIE`：夸克网盘 Cookie（必须）
- `FILM_TVS_SOURCE`：源表 Excel 路径（默认 `F:\1、自媒体\3、网站\影视\影视动漫新增（0607）.xlsx`）

### 脚本自动完成：

1. 读取源表 → 匹配已有条目（按链接/title/系列名）
2. 夸克 API 读取目录结构 → 生成 `res/dirs/{key}.html`
3. 豆瓣 API 下载封面 → 保存到 `res/covers/{系列名}/{title_key}.webp`
4. 自动写 Excel（新增或更新）
5. 运行 `python py/verify_deploy.py` 验证所有目录文件完整性
6. 手动修复验证发现的问题（脱敏残留/缺失目录）
7. 运行 `python py/generate_html.py` 生成网站
8. 自动 `git commit + push`

## 四、特殊情况处理

### 标题显示不全
修改 `templates/card-tpl.html`：去掉 `text-truncate` 类，改用 `word-break: break-word`

### API 无法访问特殊字符文件夹
百度网盘 API 对 `A 爱情公寓` 等带空格/特殊字符的路径可能失败，手动创建菜单文件到 `res/baidu-menus/` 目录。

### 封面不匹配
先尝试精确匹配（`normalize()` 去空格特殊字符对比），再模糊匹配（中文 Jaccard 相似度 >0.5）。仍失败则从 `F:\1、自媒体\3、网站\影视\缺失封面\` 手动替换。

### 热点封面与子页面封面分离
- 子页面封面：`res/covers/{系列名}/{标题key}.webp`
- 热点封面：`res/hot-covers/{标题}.jpg`（独立目录，避免互相覆盖）

### 错误归类修正
直接改 Excel 中 `所属系列` 字段，重新运行 `generate_html.py`。

## 五、文件路径速查

| 用途 | 路径 |
|------|------|
| 数据源 | `res/data_new.xlsx`（4 sheets） |
| 配置 | `res/README.md`（标题/SEO/热点） |
| 子页面封面 | `res/covers/` |
| 热点封面 | `res/hot-covers/` |
| 百度网盘菜单 | `res/baidu-menus/tv/` 和 `res/baidu-menus/movie/` |
| 夸克网盘目录 | `res/dirs/` |
| HTML 生成器 | `py/generate_html.py` |
| 交互式上架脚本 | `py/listing.py` |
| 批量上架脚本 | `py/batch_list.py` |
| 卡片模板 | `templates/card-tpl.html` |
| 子页面模板 | `templates/section-tpl.html` |
| 首页模板 | `templates/index-tpl.html` |
| 输出目录 | `sections/`（section-01/02/03.html） |
| 用户封面目录 | `F:\1、自媒体\3、网站\影视\缺失封面\` |
