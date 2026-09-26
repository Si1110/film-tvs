/**
 * CDN 配置文件
 * 用于加速 GitHub Pages 上的静态资源加载
 */

(function() {
    'use strict';

    // ========== CDN 配置 ==========
    const CDN_CONFIG = {
        // 是否启用 CDN
        enabled: false,
        
        // CDN 提供商选择
        // 'jsdelivr' - jsDelivr (推荐，免费，国内访问较快)
        // 'ghproxy' - ghproxy.com (GitHub 文件代理)
        // 'fastgit' - FastGit (GitHub 加速)
        // 'statically' - Statically (图片优化CDN)
        // 'local' - 使用本地路径（开发环境）
        provider: 'jsdelivr',
        
        // GitHub 仓库信息
        github: {
            user: 'Si1110',           // 你的 GitHub 用户名
            repo: 'film-tvs',            // 仓库名
            branch: 'res'               // 分支名（main, master, res 等）
        },
        
        // CDN 提供商的 URL 模板
        providers: {
            // jsDelivr - 最推荐，全球CDN，支持npm、GitHub等
            jsdelivr: 'https://cdn.jsdelivr.net/gh/{user}/{repo}@{branch}',
            
            // ghproxy - GitHub 文件代理服务
            ghproxy: 'https://ghproxy.com/https://raw.githubusercontent.com/{user}/{repo}/{branch}',
            
            // FastGit - GitHub 加速服务（国内）
            fastgit: 'https://raw.fastgit.org/{user}/{repo}/{branch}',
            
            // Statically - 支持图片优化
            statically: 'https://cdn.statically.io/gh/{user}/{repo}/{branch}',
            
            // 本地路径（开发环境）
            local: ''
        }
    };

    // ========== 生成 CDN 基础 URL ==========
    function getCDNBaseURL() {
        if (!CDN_CONFIG.enabled || CDN_CONFIG.provider === 'local') {
            return '';
        }

        const template = CDN_CONFIG.providers[CDN_CONFIG.provider];
        if (!template) {
            console.warn(`未知的CDN提供商: ${CDN_CONFIG.provider}，使用本地路径`);
            return '';
        }

        return template
            .replace('{user}', CDN_CONFIG.github.user)
            .replace('{repo}', CDN_CONFIG.github.repo)
            .replace('{branch}', CDN_CONFIG.github.branch);
    }

    // ========== 转换路径为 CDN 路径 ==========
    function toCDNPath(localPath) {
        if (!CDN_CONFIG.enabled) {
            return localPath;
        }

        const cdnBase = getCDNBaseURL();
        if (!cdnBase) {
            return localPath;
        }

        // 移除路径开头的 ./ 或 ../
        let cleanPath = localPath;
        
        // 处理相对路径
        if (cleanPath.startsWith('../')) {
            // 从 sections/ 页面引用，去掉 ../
            cleanPath = cleanPath.substring(3);
        } else if (cleanPath.startsWith('./')) {
            // 从根目录引用，去掉 ./
            cleanPath = cleanPath.substring(2);
        }

        return `${cdnBase}/${cleanPath}`;
    }

    // ========== 替换页面中的图片 URL ==========
    function replaceImageURLs() {
        const images = document.querySelectorAll('img[src]');
        let replacedCount = 0;

        images.forEach(img => {
            const originalSrc = img.getAttribute('src');
            
            // 只处理本地资源（不处理外部 URL）
            if (originalSrc && !originalSrc.startsWith('http') && !originalSrc.startsWith('//')) {
                const cdnSrc = toCDNPath(originalSrc);
                if (cdnSrc !== originalSrc) {
                    img.setAttribute('src', cdnSrc);
                    img.setAttribute('data-original-src', originalSrc); // 保存原始路径
                    replacedCount++;
                }
            }
        });

        console.log(`✅ CDN已启用 [${CDN_CONFIG.provider}]: 已替换 ${replacedCount} 张图片`);
        console.log(`📍 CDN Base URL: ${getCDNBaseURL()}`);
    }

    // ========== 替换 CSS/JS 等资源 URL ==========
    function replaceResourceURLs() {
        // 替换 link 标签 (CSS)
        const links = document.querySelectorAll('link[href]');
        links.forEach(link => {
            const originalHref = link.getAttribute('href');
            if (originalHref && !originalHref.startsWith('http') && !originalHref.startsWith('//')) {
                const cdnHref = toCDNPath(originalHref);
                if (cdnHref !== originalHref) {
                    link.setAttribute('href', cdnHref);
                    link.setAttribute('data-original-href', originalHref);
                }
            }
        });

        // 注意：script 标签不在此处替换，因为脚本已经加载
    }

    // ========== 监听动态添加的图片 ==========
    function observeNewImages() {
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) { // Element node
                        // 检查是否是图片
                        if (node.tagName === 'IMG') {
                            const src = node.getAttribute('src');
                            if (src && !src.startsWith('http') && !src.startsWith('//')) {
                                node.setAttribute('src', toCDNPath(src));
                            }
                        }
                        // 检查子元素中的图片
                        const imgs = node.querySelectorAll('img[src]');
                        imgs.forEach(img => {
                            const src = img.getAttribute('src');
                            if (src && !src.startsWith('http') && !src.startsWith('//')) {
                                img.setAttribute('src', toCDNPath(src));
                            }
                        });
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // ========== 错误回退处理 ==========
    function setupErrorFallback() {
        document.addEventListener('error', function(e) {
            if (e.target.tagName === 'IMG') {
                const img = e.target;
                const originalSrc = img.getAttribute('data-original-src');
                
                // 如果CDN加载失败，回退到原始路径
                if (originalSrc && img.src !== originalSrc) {
                    console.warn(`CDN 图片加载失败，回退到本地: ${img.src}`);
                    img.src = originalSrc;
                }
            }
        }, true);
    }

    // ========== 导出工具函数 ==========
    window.CDN = {
        config: CDN_CONFIG,
        getBaseURL: getCDNBaseURL,
        toPath: toCDNPath,
        
        // 手动启用/禁用 CDN
        enable: function() {
            CDN_CONFIG.enabled = true;
            location.reload();
        },
        disable: function() {
            CDN_CONFIG.enabled = false;
            location.reload();
        },
        
        // 切换 CDN 提供商
        setProvider: function(provider) {
            if (CDN_CONFIG.providers[provider]) {
                CDN_CONFIG.provider = provider;
                location.reload();
            } else {
                console.error('未知的CDN提供商:', provider);
            }
        }
    };

    // ========== 页面加载完成后执行 ==========
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            if (CDN_CONFIG.enabled) {
                replaceImageURLs();
                replaceResourceURLs();
                observeNewImages();
                setupErrorFallback();
            } else {
                console.log('ℹ️ CDN 已禁用，使用本地资源');
            }
        });
    } else {
        if (CDN_CONFIG.enabled) {
            replaceImageURLs();
            replaceResourceURLs();
            observeNewImages();
            setupErrorFallback();
        }
    }

})();
