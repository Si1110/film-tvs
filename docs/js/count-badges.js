/**
 * 自动统计各 section 页面的卡片数量并更新徽章数字
 * 通过异步加载 section 页面，统计卡片数量后更新主页徽章
 */

(function() {
    'use strict';

    // Section 配置：section 文件名 -> 对应的徽章元素选择器
    const SECTIONS = [
        { file: 'section-01.html', index: 0 },
        { file: 'section-02.html', index: 1 },
        { file: 'section-03.html', index: 2 }
    ];

    /**
     * 通过 fetch 加载 section 页面并统计卡片数量
     * @param {string} sectionFile - section 文件名
     * @returns {Promise<number>} 卡片数量
     */
    async function countCardsInSection(sectionFile) {
        try {
            const response = await fetch(`./sections/${sectionFile}`);
            if (!response.ok) {
                console.warn(`⚠️ 无法加载 ${sectionFile}: ${response.status}`);
                return 0;
            }

            const html = await response.text();
            
            // 使用正则表达式统计卡片数量（更可靠）
            const pattern = /<div\s+class="card\s+mb-3\s+bold-border"/gi;
            const matches = html.match(pattern);
            return matches ? matches.length : 0;
        } catch (error) {
            console.error(`❌ 统计 ${sectionFile} 时出错:`, error);
            return 0;
        }
    }

    /**
     * 更新指定徽章的数字
     * @param {number} index - 徽章索引（0-7）
     * @param {number} count - 卡片数量
     */
    function updateBadge(index, count) {
        // 获取所有徽章元素
        const badges = document.querySelectorAll('.section-badge');
        
        if (index < 0 || index >= badges.length) {
            console.warn(`⚠️ 徽章索引 ${index} 超出范围`);
            return;
        }

        const badge = badges[index];
        const oldText = badge.textContent;
        
        // 保留原有格式（如 "82+ 部" 中的 "+"）
        const hasPlus = oldText.includes('+');
        const newText = hasPlus ? `${count}+ 部` : `${count} 部`;
        
        // 更新徽章文本
        badge.textContent = newText;
        
        console.log(`✓ 更新徽章 [${index}]: ${oldText} → ${newText}`);
    }

    /**
     * 统计所有 section 并更新徽章
     */
    async function updateAllBadges() {
        console.log('📊 开始统计各 section 页面的卡片数量...');
        
        const startTime = performance.now();
        
        // 并行加载所有 section 页面
        const promises = SECTIONS.map(async (section) => {
            const count = await countCardsInSection(section.file);
            updateBadge(section.index, count);
            return { file: section.file, count };
        });

        // 等待所有统计完成
        const results = await Promise.all(promises);
        
        const endTime = performance.now();
        const duration = (endTime - startTime).toFixed(2);
        
        console.log('✨ 徽章统计完成！');
        console.log(`⏱️ 耗时: ${duration}ms`);
        console.log('📈 统计结果:');
        results.forEach(r => {
            console.log(`   ${r.file} → ${r.count} 部`);
        });
    }

    // 页面加载完成后自动执行统计
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', updateAllBadges);
    } else {
        // DOM 已经加载完成，直接执行
        updateAllBadges();
    }

    // 暴露到全局（方便调试）
    window.updateAllBadges = updateAllBadges;

})();
