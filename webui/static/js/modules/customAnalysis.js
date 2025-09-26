// 自定义分析模块
export function setupCustomAnalysis() {
    const runBtn = document.getElementById('run-custom-analysis');

    if (runBtn) {
        runBtn.addEventListener('click', function() {
            const module = document.getElementById('custom-module').value;
            const params = document.getElementById('custom-params').value;

            if (!module) {
                alert('请选择分析模块');
                return;
            }

            runCustomAnalysis(module, params);
        });
    }
}

function runCustomAnalysis(module, params) {
    if (!window.currentAnalysisId) {
        alert('请先分析一个文件');
        return;
    }

    try {
        // 解析参数
        const parsedParams = params ? JSON.parse(params) : {};

        // 发送自定义分析请求
        fetch('/run-custom-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                analysis_id: window.currentAnalysisId,
                module: module,
                params: parsedParams
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('自定义分析执行成功');
                // 根据模块类型刷新相应视图
                refreshModuleView(module);
            } else {
                alert(`自定义分析失败: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('自定义分析请求失败:', error);
            alert('自定义分析请求失败');
        });

    } catch (e) {
        alert('参数格式错误，请输入有效的JSON');
    }
}

function refreshModuleView(module) {
    switch (module) {
        case 'http_analysis':
            // 刷新HTTP分析视图
            break;
        case 'dns_analysis':
            // 刷新DNS分析视图
            break;
        case 'tcp_analysis':
            // 刷新TCP分析视图
            break;
        default:
            break;
    }
}