/**
 * 全局搜索功能 - 搜索所有 section 页面中的电影/剧集卡片
 * 支持搜索电影名称和简介，最多显示前 9 个匹配结果
 */

(function() {
    'use strict';

    // 检测当前页面路径，判断是主页还是 section 页面
    const isIndexPage = !window.location.pathname.includes('/sections/');
    const sectionsPath = isIndexPage ? './sections/' : './';

    // Section 配置
    const SECTIONS = [
        { file: 'section-01.html', name: '剧集资源' },
        { file: 'section-02.html', name: '电影资源' },
        { file: 'section-03.html', name: '动漫资源' }
    ];

    const MAX_RESULTS = 9; // 最多显示 9 个结果

    /**
     * 从 HTML 中提取卡片信息
     * @param {string} html - section 页面的 HTML 内容
     * @param {string} sectionName - section 名称
     * @param {string} sectionFile - section 文件名
     * @returns {Array} 卡片信息数组
     */
    function extractCards(html, sectionName, sectionFile) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const cards = [];

        // 查找所有卡片（实际 HTML 结构：.card.h-100.shadow-sm.border-0）
        const cardElements = doc.querySelectorAll('.card.h-100.shadow-sm.border-0');
        
        var seen = {};
        cardElements.forEach(function(card) {
            try {
                var titleElement = card.querySelector('.card-title');
                var title = titleElement ? titleElement.textContent.trim() : '';

                // 生成锚点ID（与 add-card-anchors.js 算法一致）
                var baseAnchor = title ? 'card-' + title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '-').substring(0, 50) : '';
                var count = seen[baseAnchor] || 0;
                seen[baseAnchor] = count + 1;
                var anchorId = count > 0 ? baseAnchor + '-' + count : baseAnchor;

                // 提取简介
                var descElement = card.querySelector('.desc-text');
                var description = descElement ? descElement.textContent.trim() : '';

                // 提取缩略图
                var imgElement = card.querySelector('img.card-img');
                var thumbnail = imgElement ? imgElement.getAttribute('src') : '';

                // 提取语言和字幕信息
                var language = '';
                var subtitle = '';
                var badges = card.querySelectorAll('.badge.bg-light.text-dark.border');
                badges.forEach(function(b) {
                    var icon = b.querySelector('.bi-translate, .bi-subtitles');
                    if (icon) {
                        var text = b.textContent.trim();
                        if (icon.classList.contains('bi-translate')) {
                            language = text;
                        } else if (icon.classList.contains('bi-subtitles')) {
                            subtitle = text;
                        }
                    }
                });

                if (title) {
                    cards.push({
                        title: title,
                        anchorId: anchorId,
                        description: description,
                        thumbnail: thumbnail,
                        language: language,
                        subtitle: subtitle,
                        sectionName: sectionName,
                        sectionFile: sectionFile
                    });
                }
            } catch (error) {
                console.warn('解析卡片时出错:', error);
            }
        });

        return cards;
    }

    /**
     * 搜索所有 section 中的卡片
     * @param {string} keyword - 搜索关键字
     * @returns {Promise<Array>} 匹配的卡片数组
     */
    async function searchAllSections(keyword) {
        if (!keyword || keyword.trim().length === 0) {
            return [];
        }

        const keywordLower = keyword.toLowerCase();
        const allCards = [];

        // 并行加载所有 section 页面
        const promises = SECTIONS.map(async (section) => {
            try {
                const response = await fetch(`${sectionsPath}${section.file}`);
                if (!response.ok) {
                    console.warn(`无法加载 ${section.file}`);
                    return [];
                }

                const html = await response.text();
                return extractCards(html, section.name, section.file);
            } catch (error) {
                console.error(`加载 ${section.file} 时出错:`, error);
                return [];
            }
        });

        const results = await Promise.all(promises);
        results.forEach(cards => allCards.push(...cards));

        // 过滤匹配的卡片（搜索标题和简介）
        const matchedCards = allCards.filter(card => {
            const titleMatch = card.title.toLowerCase().includes(keywordLower);
            const descMatch = card.description.toLowerCase().includes(keywordLower);
            return titleMatch || descMatch;
        });

        // 只返回前 9 个结果
        return matchedCards.slice(0, MAX_RESULTS);
    }

    /**
     * 渲染搜索结果
     * @param {Array} results - 搜索结果数组
     * @param {string} keyword - 搜索关键字
     */
    function renderSearchResults(results, keyword) {
        const resultsContainer = document.getElementById('searchResults');
        const modalTitle = document.getElementById('searchModalLabel');

        if (results.length === 0) {
            modalTitle.textContent = '搜索结果';
            resultsContainer.innerHTML = `
                <div class="text-center text-muted py-5">
                    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
                        <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
                    </svg>
                    <p class="mt-3">未找到包含 "<strong>${keyword}</strong>" 的内容</p>
                    <small>请尝试其他关键字</small>
                </div>
            `;
            return;
        }

        modalTitle.textContent = `找到 ${results.length} 个结果`;

        // 渲染卡片
        let html = '<div class="row">';
        results.forEach((card, index) => {
            // 高亮显示关键字
            const highlightedTitle = highlightKeyword(card.title, keyword);
            
            // 截断简介到 100 字符
            let displayDesc = card.description.length > 100 
                ? card.description.substring(0, 100) + '...' 
                : card.description;
            const highlightedDesc = highlightKeyword(displayDesc, keyword);

            // 修正缩略图路径
            let thumbnailPath = card.thumbnail;
            if (thumbnailPath) {
                // 如果在主页，添加 sections/ 前缀；如果在 section 页面，保持不变
                thumbnailPath = isIndexPage ? `./sections/${thumbnailPath}` : thumbnailPath;
            }

            // 修正跳转链接，添加锚点
            const sectionLink = isIndexPage ? `./sections/${card.sectionFile}#${card.anchorId}` : `./${card.sectionFile}#${card.anchorId}`;
            
            // 判断是否是当前页面
            const isCurrentPage = !isIndexPage && window.location.pathname.includes(card.sectionFile);

            html += `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card h-100">
                        ${thumbnailPath ? `<img src="${thumbnailPath}" class="card-img-top" alt="${card.title}" style="height: 150px; object-fit: cover;">` : ''}
                        <div class="card-body">
                            <h6 class="card-title" style="color: #000; background: none; padding: 0; margin-bottom: 10px;">${highlightedTitle}</h6>
                            <p class="card-text small text-muted">${highlightedDesc}</p>
                            <div class="d-flex justify-content-between align-items-center mt-2">
                                <small class="text-muted">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16">
                                        <path d="M9.293 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V4.707A1 1 0 0 0 13.707 4L10 .293A1 1 0 0 0 9.293 0zM9.5 3.5v-2l3 3h-2a1 1 0 0 1-1-1zM4.5 9a.5.5 0 0 1 0-1h7a.5.5 0 0 1 0 1h-7zM4 10.5a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5zm.5 2.5a.5.5 0 0 1 0-1h4a.5.5 0 0 1 0 1h-4z"/>
                                    </svg>
                                    ${card.sectionName}
                                </small>
                                <a href="${sectionLink}" 
                                   class="btn btn-sm btn-outline-primary search-result-link" 
                                   data-anchor="${card.anchorId}"
                                   data-current-page="${isCurrentPage}">查看详情</a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        resultsContainer.innerHTML = html;
        
        // 为所有"查看详情"按钮绑定点击事件
        bindSearchResultLinks();
    }

    /**
     * 为搜索结果链接绑定点击事件
     * 如果点击的是当前页面的卡片，关闭模态框并滚动到位置
     */
    function bindSearchResultLinks() {
        const links = document.querySelectorAll('.search-result-link');
        
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                const isCurrentPage = this.getAttribute('data-current-page') === 'true';
                
                if (isCurrentPage) {
                    // 当前页面：阻止默认跳转，关闭模态框，滚动到锚点
                    e.preventDefault();
                    
                    const anchorId = this.getAttribute('data-anchor');
                    const targetElement = document.getElementById(anchorId);
                    
                    if (targetElement) {
                        // 关闭搜索模态框
                        const modal = bootstrap.Modal.getInstance(document.getElementById('searchModal'));
                        if (modal) {
                            modal.hide();
                        }
                        
                        // 等待模态框关闭动画完成后再滚动
                        setTimeout(() => {
                            // 更新 URL hash（不触发页面跳转）
                            history.pushState(null, null, `#${anchorId}`);
                            
                            // 滚动到目标位置
                            targetElement.scrollIntoView({ 
                                behavior: 'smooth', 
                                block: 'center' 
                            });
                            
                            // 添加高亮效果
                            targetElement.style.transition = 'all 0.5s ease';
                            targetElement.style.boxShadow = '0 0 20px rgba(212, 175, 55, 0.8)';
                            targetElement.style.transform = 'scale(1.02)';
                            
                            // 2秒后移除高亮
                            setTimeout(() => {
                                targetElement.style.boxShadow = '';
                                targetElement.style.transform = '';
                            }, 2000);
                        }, 300);
                    }
                } else {
                    // 跨页面：正常跳转（会打开新页面）
                    // 不需要做任何处理，浏览器默认行为
                }
            });
        });
    }

    /**
     * 高亮显示关键字
     * @param {string} text - 原文本
     * @param {string} keyword - 关键字
     * @returns {string} 高亮后的 HTML
     */
    function highlightKeyword(text, keyword) {
        if (!text || !keyword) return text;

        const regex = new RegExp(`(${escapeRegex(keyword)})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    /**
     * 转义正则表达式特殊字符
     * @param {string} str - 字符串
     * @returns {string} 转义后的字符串
     */
    function escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    /**
     * 执行搜索
     */
    async function performSearch() {
        const input = document.getElementById('globalSearchInput');
        const keyword = input.value.trim();

        if (!keyword) {
            alert('请输入搜索关键字');
            return;
        }

        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('searchModal'));
        modal.show();

        // 显示加载状态
        const resultsContainer = document.getElementById('searchResults');
        resultsContainer.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">搜索中...</span>
                </div>
                <p class="mt-3 text-muted">正在搜索 "${keyword}"...</p>
            </div>
        `;

        try {
            // 执行搜索
            const results = await searchAllSections(keyword);
            
            // 渲染结果
            renderSearchResults(results, keyword);

            console.log(`🔍 搜索 "${keyword}" 完成，找到 ${results.length} 个结果`);
        } catch (error) {
            console.error('搜索出错:', error);
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <strong>搜索出错：</strong>${error.message}
                </div>
            `;
        }
    }

    // 绑定事件
    document.addEventListener('DOMContentLoaded', function() {
        const searchBtn = document.getElementById('globalSearchBtn');
        const searchInput = document.getElementById('globalSearchInput');

        if (searchBtn) {
            searchBtn.addEventListener('click', performSearch);
        }

        if (searchInput) {
            // 回车键触发搜索
            searchInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault(); // 防止表单提交
                    performSearch();
                }
            });

            const params = new URLSearchParams(window.location.search);
            const query = params.get('q');
            if (query) {
                searchInput.value = query;
                const heroInput = document.getElementById('heroSearchInput');
                if (heroInput) heroInput.value = query;
                performSearch();
            }
        }
    });

    // 暴露到全局（方便调试）
    window.performGlobalSearch = performSearch;

})();
