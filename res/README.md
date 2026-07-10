## 说明

修改下面的变量值，运行 `python py/generate_html_from_excel.py` 脚本时会自动读取这些变量，在 python 生成网站源码的同时，自动填充 html 模板中。


### html 页面标题和提示

> 影响 `index.html`, `sections/*`

```
SITE_TITLE=山月影视库

INDEX_TITLE=📺 山月影视库 免费影视下载 📺

HEADER_EXPLANATION=电视剧、电影、动漫资源均可免费下载，支持夸克网盘、百度网盘等方式获取<br/>部分压缩资源需 <a target="_blank" href="https://www.7-zip.org/">7-Zip</a> 解压；链接失效可加 QQ 753738153 处理
```



### SEO 配置（用于优化搜索引擎推荐排名）

> 影响 `docs/js/seo-meta.js`


```
SEO_TITLE=山月影视库 - 免费影视资源下载 | 电视剧电影动漫合集

SEO_DESCRIPTION=山月影视库提供免费影视资源下载，收录电视剧、电影、动漫和热门系列合集，支持夸克网盘、百度网盘获取，涵盖中文字幕、高清 MP4/MKV、日剧、港剧、经典电影与番剧。

SEO_KEYWORDS=免费影视下载,免费电视剧下载,免费电影下载,免费动漫下载,影视资源下载,夸克网盘影视,百度网盘影视,中文字幕,高清下载,mp4下载,mkv下载,经典影视,电视剧资源,电影资源,动漫资源,日剧下载,港剧下载,国产剧下载,番剧下载,动漫合集,电影合集,Fate,刀剑神域,哈利波特,柯南剧场版,世界奇妙物语,火影忍者,海贼王,魔卡少女樱,生化危机,死神来了

SEO_AUTHOR=山月影视库

SEO_SITE_NAME=山月影视库

SEO_DOMAIN=https://si1110.github.io/film-tvs/

SEO_IMAGE=https://si1110.github.io/film-tvs/docs/movies.png

SEO_LOCALE=zh_CN

# 热点推荐配置
# HOT_ITEMS_TV/MOVIE: 按条目标题匹配（用于单视频条目），
# HOT_SERIES_ANIME: 按系列名匹配（需与 Excel 所属系列列一致）
HOT_ITEMS_TV=西游记 (1996),神探狄仁杰,识骨寻踪

HOT_ITEMS_MOVIE=哪吒之魔童降世,给阿嬷的情书,阿凡达

HOT_SERIES_ANIME=数码暴龙系列,魔卡少女樱系列,三大民工漫
```

