# FilmTVs 数据流水线知识库

## 排序系统演进

### 已知排序问题历史

#### 问题一：CI 找不到排序参考表
- **根因**：generate_html.py 硬编码本地路径 `F:\1、自媒体\3、网站\影视\影视动漫新增（0610）.xlsx`
- **修复**：将 0610.xlsx 复制到仓库 `res/`，改相对路径 `./res/影视动漫新增（0610）.xlsx`
- **教训**：所有文件引用必须使用仓库内相对路径

#### 问题二：合集与子集被分到不同系列
- **根因**：batch_list.py 对"已有条目"保留原系列，对"新增条目"按 0610 区段分配系列。当同一个主题（如唐朝诡事录）已有条目在国产精品系列、新增衍生剧在侦探悬疑系列时，就被拆散了
- **修复**：手动将神探狄仁杰、唐朝诡事录、御赐小仵作系列归到侦探悬疑系列
- **教训**：新增条目时需检测标题前缀是否匹配已有条目，继承其系列

#### 问题三：同名条目跨区段污染排序位置
- **根因**：0610.xlsx 中"射雕英雄传 (1994)"同时出现在国产精品区（Row 69）和港台剧精选区（Row 307）。旧版全局 order_map 只记录首次出现位置（Row 69），导致港台剧精选区中它排在 TVB金庸武侠合集（Row 306）之前
- **修复**：order_map 改为按区段分组 `{section_name → {title → position}}`，排序时只查同区段位置
- **教训**：同一标题在不同区段出现在 0610 表中时，必须按区段隔离排序

#### 问题四：特别篇/番外篇产生孤立主题，合集被排到子集后面
- **根因**：`extract_theme()` 只删除 `特别篇`/`番外篇` 关键词，但保留前面描述词（如 `万圣节`），导致 `9号秘事 万圣节特别篇` 得到主题 `9号秘事 万圣节`而非 `9号秘事`。孤立主题行号大（新条目），排序时先于主主题渲染，合集落后于子集
- **修复**：`\s*[：:].*` 移到 `特别篇` 匹配前执行；`特别篇` 改用 `(?:\s+[\u4e00-\u9fff]{1,15})?(?:特别篇|番外篇|...)` 连带前面描述词一起删除
- **验证方式**：`python py/check_themes.py`（检查各主题是否同时包含合集和子集）+ `python py/verify_order.py`（检查 HTML 输出中合集是否在子集前）
- **教训**：`extract_theme` 剥离后缀时必须考虑前面可能附着描述词（如 `万圣节`、`圣诞`、`电影`），用可选前缀匹配一并清除

### 当前排序逻辑（generate_html.py）— V2 扁平排序

```
1. 给每行数据标记 _row_idx（Excel 行号）
2. extract_theme() 提取标题前缀（去合集标记【】、年份、数字后缀）
3. 按主题分组，每组用最大行号定位（最新主题优先）
4. 组内排序：合集(含【】)优先，其次按标题字母序
5. 展平输出到卡片网格
```

### 验证脚本

#### 一键验证（推荐）
```bash
python py/deploy_check.py
```
自动运行：HTML 生成 → 排序验证 → BOM 检查 → CSS Grid 检查。退出码 0=通过。

#### 独立脚本
- `python py/verify_sort.py` — 排序验证（含孤立主题检测 + HTML 输出排序检查）
- `python py/generate_html.py` — 仅生成 HTML

#### 检查项
- 合集子集系列一致性（标题前缀匹配检查）
- 同名跨系列检测（区分同链接错误 vs 不同链接合法）
- 必填字段完整性
- 孤立主题检测：extract_theme 未能归一化的标题（如`万圣节特别篇`→独立主题）
- HTML 排序验证：读取生成的文件，确认每组合集在子集之前
- BOM 污染检测：模板文件是否带入 BOM 字节
- CSS Grid 布局：确认 card-grid 使用 `display: grid` 而非 Flexbox `row g-3`

### 批量新增注意事项（batch_list.py）
1. `find_matching_row` 优先级：链接精确匹配 > 标题+链接联合匹配 > 系列名匹配
2. 同一标题但不同链接 → 作为 NEW 而非 UPDATE
3. `find_series_for_new` 检测标题前缀匹配，继承已有条目系列

### 数据文件路径
- 数据文件：`res/data_new.xlsx`
- 排序参考：`res/影视动漫新增（0610）.xlsx`
- 默认源表（批量脚本）：`F:\1、自媒体\3、网站\影视\影视动漫新增（0607）.xlsx`
- 封面目录：`res/covers/{系列名}/{标题}.jpg`
- 夸克目录文件：`res/dirs/quark_{pwd_id}.html`
- 网站配置：`res/README.md`
- 模板目录：`templates/`

## Section 页面现代版重构（2026-06-14）

### 触发需求
去掉系列分栏、添加三行筛选导航（地区/类型/语言）、展平卡片网格、按添加时间排列。

### 涉及文件
| 文件 | 角色 |
|------|------|
| `res/data_new.xlsx` | 数据源，新增`类型`和`地区`列 |
| `templates/section-tpl.html` | 页面骨架，含导航栏 CSS + 筛选 JS |
| `templates/card-tpl.html` | 单张卡片模板，含类型标签 + data 属性 |
| `py/generate_html.py` | 生成脚本，`generate_section()` 核心改写 |
| `docs/css/style.css` | 全局样式，需检查是否有冲突 |

### 修改步骤复盘

#### Step 1：数据增强
- 新增`类型`列：从标题关键词推断（古装/悬疑/喜剧/犯罪/奇幻/剧情/爱情/惊悚）
- 新增`地区`列：从语言+标题关键词推断（大陆/香港/日本/欧美/韩国）
- 多类型用 `/` 分隔（如"古装/悬疑"），JS 用 `indexOf` 匹配

#### Step 2：模板修改
- `card-tpl.html`：卡片外层加 `data-genre data-region data-lang`；语言徽章后加 `genre-badge` 标签
- `section-tpl.html`：移除 group-header/TOC/查看更多；添加 `.filter-bar`（3 行 sticky 导航）+ 筛选 JS + CSS Grid 网格

#### Step 3：生成脚本修改
- `generate_section()`：去掉 0610 order_map 加载 + 分组逻辑，改为 theme-group 扁平排序
- 传递 `total_count` 和 `section_content` 给模板

#### Step 4：排序修正
- **V1（有 bug）**：直接 `(-row_idx, heji_prio, title)` 排序 → 合集先添加（行号小）被排到子集后面
- **V2（修复）**：`extract_theme()` 按主题前缀分组 → 组内合集优先 → 组按最新行号排序

### 已知陷阱

#### 陷阱 1：Flexbox + display:none → 布局混乱
- **表现**：初始加载 485 张卡片整齐，点击导航筛选后卡片大小不一、犬牙交错
- **根因**：Flexbox 的 `align-items:stretch` 给每张卡片拉伸到行高。筛选时 `display:none` 移除卡片后，剩余卡片被重排到新行，但**保留原行高度**，导致错位
- **修复**：改用 `display: grid` + `grid-template-columns: repeat(3, 1fr)`。CSS Grid 的 `display:none` 不触发此 bug
- **验证方式**：浏览器打开 section-01.html → 点击导航按钮 → 检查网格是否对齐

#### 陷阱 2：模板 BOM 污染
- **表现**：每个卡片前出现 U+FEFF（零宽不换行空格）
- **根因**：`templates/card-tpl.html` 文件以 BOM（EF BB BF）开头，Jinja2 渲染时每个卡片都带上
- **修复**：用 Python 读取并移除 BOM（`content.replace(b'\xef\xbb\xbf', b'')`）
- **验证方式**：`python -c "with open('sections/section-01.html','rb') as f: c=f.read(); print('bom:', c[:3]==b'\xef\xbb\xbf', 'count:', c.count(b'\xef\xbb\xbf'))"`

### 核心架构决策

#### CSS Grid 替代 Bootstrap Flexbox Grid
```css
.card-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);  /* 大屏 3 列 */
    gap: 1rem;
}
@media (max-width: 991px) { grid-template-columns: repeat(2, 1fr); }
@media (max-width: 576px) { grid-template-columns: 1fr; }
```
卡片不再依赖 `col-*` 类，直接 CSS Grid 控制。响应式断点与 Bootstrap 一致。

#### 筛选 JS
`filterCards(event, row, value)` 切换按钮状态 → `applyFilter()` 按 `activeFilter.row` 选 `data-region / data-genre / data-lang` 做 `indexOf` 匹配。三行独立筛选，一次只能激活一个。

### 验证方式
1. `python py/generate_html.py` — 无报错
2. `python py/verify_sort.py` — 通过
3. 浏览器打开 `sections/section-01.html` → 三行导航 sticky → 点击筛选 → 网格对齐
4. `git diff --stat` 检查涉及文件

### 复用 skill（电影/动漫页面优化）
`docs/skills/film-tvs-section-modernize.skill.md` 记录了完整的操作流程、陷阱和修复方案。后续对电影（section-02）或动漫（section-03）做类似修改时，先加载此 skill。

### GitHub Pages 部署
- 分支：`res`
- 自动部署：CI bot 监听 push → 无操作
- 手动触发：`python py/generate_html.py && git add . && git commit -m "msg" && git push origin res`
- 预热 URL：手动或通过 API 触发

## SEO 优化（2026-06-22）

### section 页面 description 生成规则

`py/generate_html.py` 中 `generate_section()` 的 description 生成逻辑：

```
1. 扫描该 section 所有条目的"所属系列"列
2. 统计各系列出现次数（series_counter）
3. 筛选出现 >= 3 次的系列（multi_series）
4. 若不足 3 个，降级为全量按频次排序（c >= 1）
5. 取 top 6 → desc_series（description 中列出）
6. 取 top 12 → key_series（keywords 中列出）
```

**关键点**：`key_series` 允许出现单条目系列（如 007 各影片独立的系列名），有利于长尾关键词匹配；`desc_series` 限到 top 6 且最低 3 次出现，避免 description 被过度拉长。

### Windows GBK 编码问题

- `deploy_check.py` 在 Windows 上打印 Unicode（� 等替换字符）时，`print()` 使用 GBK 编码会报 `UnicodeEncodeError`
- **临时解决**：`$env:PYTHONIOENCODING='utf-8'; python py/deploy_check.py`
- **脚本内修复**：`print(f"    {line.encode('utf-8', errors='replace').decode('utf-8')}")`

## OpenCode Large Asset Guardrails

This repository contains a large tracked static media set under `res/`.

Do not read, attach, summarize, grep, index, or include image/media assets in model context unless the user explicitly asks to inspect images. Treat these paths as generated/static assets:

- `res/covers/**`
- `res/hot-covers/**`
- `res/movie-covers/**`
- `res/**/合集封面/**`
- `res/**/*.png`
- `res/**/*.jpg`
- `res/**/*.jpeg`
- `res/**/*.webp`
- `res/**/*.gif`
- `res/**/*.avif`
- `imgs/**`
- `tmp/**`
- `logs/**`

Prefer working from source data, HTML, scripts, JSON, Excel files, section pages, and templates. When a task touches image references, edit the text/data references without loading image binaries.

Avoid opening the Review tab for mass media changes; use targeted `git diff --stat`, `git diff --name-only`, or path-limited diffs instead.