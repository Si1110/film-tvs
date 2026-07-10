// 关闭模态框
function closeModal() {
  var modalInstance = bootstrap.Modal.getInstance(document.getElementById('downloadModal'));
  if (modalInstance) {
    modalInstance.hide();
  }
}

// 复制到剪贴板
function copyToClipboard(elementId, event) {
  // 如果没有传递 event 参数，使用 window.event
  if (!event) {
    event = window.event;
  }
  
  const text = document.getElementById(elementId).textContent;
  
  // 使用现代的 Clipboard API
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(function() {
      // 显示复制成功提示
      const button = event.target.closest('button');
      const originalHTML = button.innerHTML;
      button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16"><path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/></svg> 已复制';
      button.classList.add('btn-success');
      button.classList.remove('btn-outline-secondary');
      
      setTimeout(function() {
        button.innerHTML = originalHTML;
        button.classList.remove('btn-success');
        button.classList.add('btn-outline-secondary');
      }, 2000);
    }).catch(function(err) {
      console.error('复制失败:', err);
      alert('复制失败，请手动复制：' + text);
    });
  } else {
    // 降级方案：使用旧的 execCommand 方法
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
      const successful = document.execCommand('copy');
      if (successful) {
        const button = event.target.closest('button');
        const originalHTML = button.innerHTML;
        button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16"><path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/></svg> 已复制';
        button.classList.add('btn-success');
        button.classList.remove('btn-outline-secondary');
        
        setTimeout(function() {
          button.innerHTML = originalHTML;
          button.classList.remove('btn-success');
          button.classList.add('btn-outline-secondary');
        }, 2000);
      } else {
        alert('复制失败，请手动复制：' + text);
      }
    } catch (err) {
      console.error('复制失败:', err);
      alert('复制失败，请手动复制：' + text);
    }
    document.body.removeChild(textarea);
  }
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
  // 下载模态框事件监听
  document.getElementById('downloadModal').addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const modalUUID = button.getAttribute('data-uuid');
    const downloadInfo = document.getElementById('downloadInfo');
    const downloadUrl = button.getAttribute('data-bs-download');
    
    let extractCode = '0000';
    try {
      const url = new URL(downloadUrl);
      extractCode = url.searchParams.get('pwd') || '0000';
    } catch (e) {
      extractCode = '0000';
    }

    downloadInfo.style.display = 'block';
    document.getElementById('modalDownloadLink').href = downloadUrl;
    document.getElementById('modalExtractCode').textContent = extractCode;
    document.getElementById('modalUUID').textContent = modalUUID;
  });

  // 激活 Tooltip
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});
