// SQL注入检测模块
export function setupSqlInjection() {
    const refreshBtn = document.getElementById('refresh-sql');

    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            if (window.currentAnalysisId) {
                loadSqlDetections(window.currentAnalysisId);
            }
        });
    }
}

export async function loadSqlDetections(analysisId) {
    try {
        const response = await fetch(`/analysis/${analysisId}/sql-detections`);
        const data = await response.json();

        // 更新检测计数
        const sqlCountElement = document.getElementById('sql-count');
        const sqlDetectionCountElement = document.getElementById('sql-detection-count');

        if (sqlCountElement) sqlCountElement.textContent = data.detections.length;
        if (sqlDetectionCountElement) sqlDetectionCountElement.textContent = data.detections.length;

        // 填充检测表格
        populateSqlDetectionTable(data.detections);

    } catch (error) {
        console.error('加载SQL注入检测失败:', error);
    }
}

// 填充SQL注入检测表格
function populateSqlDetectionTable(detections) {
    const tableBody = document.getElementById('sql-detection-table');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    // 限制显示的行数
    const maxRows = 10;
    const displayDetections = detections.slice(0, maxRows);

    displayDetections.forEach((det, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${det.time}</td>
            <td>${det.src}</td>
            <td>${det.dst}</td>
            <td><code>${det.pattern}</code></td>
            <td>
                <button class="btn btn-sm btn-outline-primary view-details" data-index="${index}">
                    <i class="bi bi-search"></i> 详情
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });

    // 如果检测数量超过最大行数，显示提示
    if (detections.length > maxRows) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="5" class="text-center text-muted">
                还有 ${detections.length - maxRows} 个检测未显示
            </td>
        `;
        tableBody.appendChild(row);
    }
}