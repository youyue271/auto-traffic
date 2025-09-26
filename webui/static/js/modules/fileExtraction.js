// 文件提取模块
export function setupFileExtraction() {
    const refreshBtn = document.getElementById('refresh-files');

    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            if (window.currentAnalysisId) {
                loadExtractedFiles(window.currentAnalysisId);
            }
        });
    }
}

export async function loadExtractedFiles(analysisId) {
    try {
        const response = await fetch(`/analysis/${analysisId}/extracted-files`);
        const data = await response.json();

        // 更新文件计数
        const fileCountElement = document.getElementById('file-count');
        if (fileCountElement) fileCountElement.textContent = data.files.length;

        // 填充文件网格
        populateFileGrid(data.files);

    } catch (error) {
        console.error('加载提取文件失败:', error);
    }
}

// 填充文件网格
function populateFileGrid(files) {
    const fileGrid = document.getElementById('file-grid');
    if (!fileGrid) return;

    fileGrid.innerHTML = '';

    // 限制显示的文件数量
    const maxFiles = 12;
    const displayFiles = files.slice(0, maxFiles);

    displayFiles.forEach(file => {
        const col = document.createElement('div');
        col.className = 'file-grid-item';
        col.innerHTML = `
            <div class="card analysis-card h-100">
                <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                        <i class="bi bi-file-earmark fs-1 me-3"></i>
                        <div>
                            <h6 class="mb-0">${file.name}</h6>
                            <small class="text-muted">${file.type}</small>
                        </div>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                        <span><i class="bi bi-hdd"></i> ${file.size}</span>
                        <span><i class="bi bi-pc"></i> ${file.src}</span>
                    </div>
                    <div class="d-grid">
                        <button class="btn btn-sm btn-outline-success">
                            <i class="bi bi-download"></i> 下载
                        </button>
                    </div>
                </div>
            </div>
        `;
        fileGrid.appendChild(col);
    });

    // 如果文件数量超过最大数量，显示提示
    if (files.length > maxFiles) {
        const col = document.createElement('div');
        col.className = 'file-grid-item';
        col.innerHTML = `
            <div class="card analysis-card h-100">
                <div class="card-body d-flex flex-column justify-content-center align-items-center">
                    <i class="bi bi-info-circle fs-1 text-muted mb-3"></i>
                    <p class="text-center mb-0">
                        还有 ${files.length - maxFiles} 个文件未显示
                    </p>
                </div>
            </div>
        `;
        fileGrid.appendChild(col);
    }
}