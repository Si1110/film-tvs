/**
 * Sitemap 生成器
 * 自动生成和更新 sitemap.xml 文件
 * 使用方法：在浏览器控制台运行 generateSitemap()
 */

(function() {
    'use strict';

    /**
     * 配置项
     */
    const config = {
        domain: 'https://yourdomain.com', // 请替换为实际域名
        defaultChangeFreq: 'monthly',
        homePriority: '1.0',
        sectionPriority: '0.9',
        othersPriority: '0.7'
    };

    /**
     * 获取所有影视系列章节
     */
    function getAllSections() {
        const sections = [];
        const sectionElements = document.querySelectorAll('h4[id^="section-"]');
        
        sectionElements.forEach(element => {
            const id = element.id;
            const title = element.textContent.trim();
            const priority = id === 'section-99' ? config.othersPriority : config.sectionPriority;
            
            sections.push({
                id: id,
                title: title,
                priority: priority
            });
        });
        
        return sections;
    }

    /**
     * 生成当前日期（YYYY-MM-DD 格式）
     */
    function getCurrentDate() {
        const date = new Date();
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    /**
     * 生成 sitemap XML 内容
     */
    function generateSitemapXML() {
        const sections = getAllSections();
        const currentDate = getCurrentDate();
        
        let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n';
        xml += '        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n';
        xml += '        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\n';
        xml += '        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n\n';
        
        // 主页
        xml += '  <!-- 主页 -->\n';
        xml += '  <url>\n';
        xml += `    <loc>${config.domain}/</loc>\n`;
        xml += `    <lastmod>${currentDate}</lastmod>\n`;
        xml += `    <changefreq>weekly</changefreq>\n`;
        xml += `    <priority>${config.homePriority}</priority>\n`;
        xml += '  </url>\n\n';
        
        // 各个系列
        sections.forEach(section => {
            xml += `  <!-- ${section.title} -->\n`;
            xml += '  <url>\n';
            xml += `    <loc>${config.domain}/#${section.id}</loc>\n`;
            xml += `    <lastmod>${currentDate}</lastmod>\n`;
            xml += `    <changefreq>${config.defaultChangeFreq}</changefreq>\n`;
            xml += `    <priority>${section.priority}</priority>\n`;
            xml += '  </url>\n\n';
        });
        
        xml += '</urlset>\n';
        
        return xml;
    }

    /**
     * 下载 sitemap.xml 文件
     */
    function downloadSitemap(content) {
        const blob = new Blob([content], { type: 'application/xml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sitemap.xml';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * 生成并下载 sitemap
     */
    function generateSitemap() {
        console.log('🚀 开始生成 sitemap.xml...');
        
        const xml = generateSitemapXML();
        
        console.log('✅ Sitemap 生成成功！');
        console.log('📄 包含以下内容：');
        console.log(`   - 主页: ${config.domain}/`);
        
        const sections = getAllSections();
        sections.forEach(section => {
            console.log(`   - ${section.title}: ${config.domain}/#${section.id}`);
        });
        
        console.log('\n📥 开始下载 sitemap.xml...');
        downloadSitemap(xml);
        
        console.log('✨ 完成！请将下载的 sitemap.xml 上传到网站根目录');
        
        return xml;
    }

    /**
     * 显示 sitemap 预览
     */
    function previewSitemap() {
        const xml = generateSitemapXML();
        console.log('📄 Sitemap 预览：\n');
        console.log(xml);
        return xml;
    }

    /**
     * 检查配置
     */
    function checkConfig() {
        console.log('⚙️ 当前配置：');
        console.log(`   域名: ${config.domain}`);
        console.log(`   更新频率: ${config.defaultChangeFreq}`);
        console.log(`   主页优先级: ${config.homePriority}`);
        console.log(`   系列优先级: ${config.sectionPriority}`);
        console.log(`   其他优先级: ${config.othersPriority}`);
        
        if (config.domain === 'https://yourdomain.com') {
            console.warn('⚠️ 警告：请先在脚本中修改 domain 为实际域名！');
        }
    }

    // 导出到全局作用域
    window.SitemapGenerator = {
        generate: generateSitemap,
        preview: previewSitemap,
        checkConfig: checkConfig,
        config: config
    };

    // 页面加载完成后自动检查配置
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkConfig);
    } else {
        checkConfig();
    }

    console.log('💡 Sitemap 生成器已加载！');
    console.log('   使用方法：');
    console.log('   - SitemapGenerator.generate() - 生成并下载 sitemap.xml');
    console.log('   - SitemapGenerator.preview() - 预览 sitemap 内容');
    console.log('   - SitemapGenerator.checkConfig() - 检查当前配置');

})();
