## 说明

修改下面的变量值，运行 `python py/generate_html_from_excel.py` 脚本时会自动读取这些变量，在 python 生成网站源码的同时，自动填充 html 模板中。


### html 页面标题和提示

> 影响 `index.html`, `sections/*`

```
SITE_TITLE=山月影视库

INDEX_TITLE=📺 山月影视库 📺

HEADER_EXPLANATION=本站部分资源下载后需 <a target="_blank" href="https://www.7-zip.org/">7-Zip</a> 工具解压<br/>如遇解压密码错误，或链接失效，可加 QQ 753738153 处理
```



### SEO 配置（用于优化搜索引擎推荐排名）

> 影响 `docs/js/seo-meta.js`


```
SEO_TITLE=山月影视库 - 经典影视资源合集

SEO_DESCRIPTION=经典影视资源导航，收录经典动漫、日剧、电影与热门系列合集，包括 Fate、刀剑神域、哈利波特、柯南剧场版、世界奇妙物语等，支持按电视剧、电影、动漫分类浏览。

SEO_KEYWORDS=90后,怀旧,经典影视,动漫合集,番剧,日本电视剧,热血动漫,治愈动漫,悬疑剧,青春剧,日本剧,Fate,Re0,刀剑神域,SAO,钢之炼金术师,死亡笔记,一拳超人,东京喰种,寄生兽,中华一番,加速世界,超速摇摇,逆境无赖,仙境传说,游戏王,头文字D,数码暴龙,世界奇妙物语,哈利波特,生化危机,火影忍者,海贼王,你的名字,声之形,疯狂动物城,柯南,金田一事件簿,轮到你了,一家之鼠,打机王,海扁王,那些年我们一起追的女孩,魔卡少女樱,死神来了,藤原龙也,伊藤润二,一公升的眼泪,只有我不存在的街道,求婚大作战,经典电影,电影下载,高清下载,中文字幕,mp4格式,视频下载

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

