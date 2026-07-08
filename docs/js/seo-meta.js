/**
 * SEO 元标签管理
 * 仅注入无法通过服务器端渲染的内容：移动端标签、hreflang、Apple Touch Icon
 * meta/og/twitter/JSON-LD 标签已在 HTML 模板中服务器端渲染，避免重复
 */
(function() {
    'use strict';

    const seoConfig = {
        title: "山月影视库 - 经典影视资源合集",
        description: "经典影视资源导航，收录经典动漫、日剧、电影与热门系列合集，包括 Fate、刀剑神域、哈利波特、柯南剧场版、世界奇妙物语等，支持按电视剧、电影、动漫分类浏览。",
        keywords: "90后,怀旧,经典影视,动漫合集,番剧,日本电视剧,热血动漫,治愈动漫,悬疑剧,青春剧,日本剧,Fate,Re0,刀剑神域,SAO,钢之炼金术师,死亡笔记,一拳超人,东京喰种,寄生兽,中华一番,加速世界,超速摇摇,逆境无赖,仙境传说,游戏王,头文字D,数码暴龙,世界奇妙物语,哈利波特,生化危机,火影忍者,海贼王,你的名字,声之形,疯狂动物城,柯南,金田一事件簿,轮到你了,一家之鼠,打机王,海扁王,那些年我们一起追的女孩,魔卡少女樱,死神来了,藤原龙也,伊藤润二,一公升的眼泪,只有我不存在的街道,求婚大作战,经典电影,电影下载,高清下载,中文字幕,mp4格式,视频下载",
        author: "山月影视库",
        siteName: "山月影视库",
        domain: "https://si1110.github.io/film-tvs/",
        image: "https://si1110.github.io/film-tvs/docs/movies.png",
        locale: "zh_CN",
        movieSeries: [
            { name: "电视剧资源", description: "精选经典电视剧作品合集。涵盖日剧、港剧、国产剧等各类经典剧集，包括世界奇妙物语、藤原龙也系列、甄嬛传、神雕侠侣等众多热门作品。全部中文字幕，高清mp4下载。" },
            { name: "电影资源", description: "精选经典电影作品合集。涵盖好莱坞大片、港片、日影等各类经典电影，包括哈利波特、生化危机、死神来了、周星驰等众多热门系列。全部中文字幕，高清mp4下载。" },
            { name: "动漫资源", description: "精选日本动漫、国产动画作品合集。涵盖热血、治愈、悬疑、科幻等各类题材，按照网络热度从高到低排列。" }
        ]
    };

    function createMetaTag(attrs) {
        const meta = document.createElement('meta');
        Object.keys(attrs).forEach(function(key) {
            meta.setAttribute(key, attrs[key]);
        });
        return meta;
    }

    function createLinkTag(attrs) {
        const link = document.createElement('link');
        Object.keys(attrs).forEach(function(key) {
            link.setAttribute(key, attrs[key]);
        });
        return link;
    }

    function insertSEOTags() {
        var head = document.head;
        var currentUrl = window.location.href.split('#')[0].split('?')[0];
        var fragment = document.createDocumentFragment();

        // 移动设备优化
        var mobileTags = [
            { name: 'mobile-web-app-capable', content: 'yes' },
            { name: 'apple-mobile-web-app-capable', content: 'yes' },
            { name: 'apple-mobile-web-app-status-bar-style', content: 'black' }
        ];
        mobileTags.forEach(function(attrs) {
            fragment.appendChild(createMetaTag(attrs));
        });

        // Apple Touch Icon
        fragment.appendChild(createLinkTag({
            rel: 'apple-touch-icon',
            href: seoConfig.domain + 'docs/favicon.png'
        }));

        head.appendChild(fragment);

    }

    insertSEOTags();

    window.SEOConfig = seoConfig;
})();
