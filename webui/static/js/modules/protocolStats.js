// 协议统计模块
export function setupProtocolStats() {
    const refreshBtn = document.getElementById('refresh-protocol');

    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            if (window.currentAnalysisId) {
                loadProtocolStats(window.currentAnalysisId);
            }
        });
    }
}

export async function loadProtocolStats(analysisId) {
    try {
        const response = await fetch(`/analysis/${analysisId}/protocol-stats`);
        const data = await response.json();

        // 填充协议统计表格
        populateProtocolTable(data.protocol_distribution);

        // 渲染图表
        renderProtocolChart(data.protocol_distribution);

    } catch (error) {
        console.error('加载协议统计失败:', error);
    }
}

// 填充协议统计表格
function populateProtocolTable(protocols) {
    const tableBody = document.getElementById('protocol-table');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    // 限制显示的行数
    const maxRows = 10;
    const displayProtocols = protocols.slice(0, maxRows);

    displayProtocols.forEach(proto => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="badge bg-primary protocol-badge">${proto.name}</span></td>
            <td>${proto.count}</td>
            <td>
                <div class="progress" style="height: 20px;">
                    <div class="progress-bar" role="progressbar" 
                         style="width: ${proto.percentage}%;">
                        ${proto.percentage}%
                    </div>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });

    // 如果协议数量超过最大行数，显示提示
    if (protocols.length > maxRows) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="3" class="text-center text-muted">
                还有 ${protocols.length - maxRows} 个协议未显示
            </td>
        `;
        tableBody.appendChild(row);
    }
}

// 渲染协议统计图表
function renderProtocolChart(protocols) {
    const ctx = document.getElementById('protocol-chart');
    if (!ctx) return;

    // 如果已有图表实例，销毁它
    if (window.protocolChart) {
        window.protocolChart.destroy();
    }

    window.protocolChart = new Chart(ctx.getContext('2d'), {
        type: 'pie',
        data: {
            labels: protocols.map(p => p.name),
            datasets: [{
                data: protocols.map(p => p.count),
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}