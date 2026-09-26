/**
 * SEO 元标签管理
 * 仅注入无法通过服务器端渲染的内容：移动端标签、hreflang、Apple Touch Icon
 * meta/og/twitter/JSON-LD 标签已在 HTML 模板中服务器端渲染，避免重复
 */
(function() {
    'use strict';

    const seoConfig = {
        title: "山月影视库 - 免费影视资源下载 | 电视剧电影动漫合集",
        description: "山月影视库提供免费影视资源下载，收录电视剧、电影、动漫和热门系列合集，支持夸克网盘、百度网盘获取，涵盖中文字幕、高清 MP4/MKV、日剧、港剧、经典电影与番剧。",
        keywords: "免费影视下载,免费电视剧下载,免费电影下载,免费动漫下载,影视资源下载,夸克网盘影视,百度网盘影视,中文字幕,高清下载,mp4下载,mkv下载,经典影视,电视剧资源,电影资源,动漫资源,日剧下载,港剧下载,国产剧下载,番剧下载,动漫合集,电影合集,Fate,刀剑神域,哈利波特,柯南剧场版,世界奇妙物语,火影忍者,海贼王,魔卡少女樱,生化危机,死神来了",
        author: "山月影视库",
        siteName: "山月影视库",
        domain: "https://si1110.github.io/film-tvs/",
        image: "https://si1110.github.io/film-tvs/docs/movies.png",
        locale: "zh_CN",
        movieSeries: [
            { name: "剧集资源", description: "电视剧资源免费下载导航。收录日剧、港剧、国产剧、悬疑剧、武侠剧等经典剧集，支持夸克网盘、百度网盘获取，提供中文字幕、高清 MP4/MKV 资源下载。" },
            { name: "电影资源", description: "电影资源免费下载导航。收录好莱坞大片、华语电影、日影、恐怖、科幻、喜剧等经典电影合集，支持夸克网盘、百度网盘获取，提供中文字幕、高清 MP4/MKV 下载。" },
            { name: "动漫资源", description: "动漫资源免费下载导航。收录日本动漫、国产动画与热门番剧合集，覆盖热血、治愈、悬疑、科幻、异世界与童年怀旧题材，支持夸克网盘、百度网盘获取。" }
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
