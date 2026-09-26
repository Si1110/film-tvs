(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        var modal = document.getElementById('collectionDirModal');
        if (!modal) return;

        var cache = {};

        modal.addEventListener('show.bs.modal', function(e) {
            var btn = e.relatedTarget;
            if (!btn) return;

            var dirKey = btn.getAttribute('data-dir-key');
            var dirTitle = btn.getAttribute('data-dir-title') || '目录';

            var label = document.getElementById('collectionDirModalLabel');
            var body = document.getElementById('collectionDirModalBody');

            if (label) label.textContent = dirTitle + ' - 目录';
            if (body) body.innerHTML = '<div class="text-center text-muted py-4"><p>加载中...</p></div>';

            if (!dirKey) {
                if (body) body.innerHTML = '<div class="text-center text-muted py-4"><p>暂无目录信息</p></div>';
                return;
            }

            // Check if it's a URL (starts with http)
            if (dirKey.match(/^https?:\/\//)) {
                // It's a URL - show as embedded link
                if (body) {
                    body.innerHTML = '<div class="text-center py-4">' +
                        '<p class="text-muted mb-3">该资源目录请前往网盘查看：</p>' +
                        '<a href="' + dirKey + '" target="_blank" class="btn btn-warning px-4 py-2" style="font-weight:600;">' +
                        '打开网盘目录 <i class="bi bi-box-arrow-up-right"></i></a>' +
                        '<p class="text-muted mt-3 small">点击后在新标签页中浏览文件列表</p>' +
                        '</div>';
                }
                return;
            }

            // Try to load from cached or fetch
            if (cache[dirKey]) {
                if (body) body.innerHTML = cache[dirKey];
                return;
            }

            var dirUrl = '../res/dirs/' + encodeURIComponent(dirKey) + '.html';
            fetch(dirUrl)
                .then(function(r) {
                    if (!r.ok) throw new Error('Not found');
                    return r.text();
                })
                .then(function(html) {
                    cache[dirKey] = html;
                    if (body) body.innerHTML = html;
                })
                .catch(function() {
                    // Fallback: show Quark link if the key contains a URL pattern
                    if (body) {
                        body.innerHTML = '<div class="text-center py-4">' +
                            '<p class="text-muted">暂无详细目录，请前往网盘查看</p>' +
                            '</div>';
                    }
                });
        });
    });

})();
