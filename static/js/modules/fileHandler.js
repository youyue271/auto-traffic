// 文件处理模块
export function setupFileHandling() {
    const dropArea = document.getElementById('file-drop-area');
    const fileInput = document.getElementById('file-input');

    if (!dropArea || !fileInput) return;

    // 点击拖放区域触发文件选择
    dropArea.addEventListener('click', () => {
        fileInput.click();
    });

    // 文件选择处理
    fileInput.addEventListener('change', function(e) {
        if (this.files.length > 0) {
            handleFile(this.files[0]);
        }
    });

    // 拖放事件处理
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropArea.classList.add('drag-over');
    }

    function unhighlight() {
        dropArea.classList.remove('drag-over');
    }

    // 处理文件拖放
    dropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const file = dt.files[0];
        handleFile(file);
    }

    // 处理文件分析
    function handleFile(file) {
        if (!file) return;

        // 验证文件类型
        const ext = file.name.split('.').pop().toLowerCase();
        if (ext !== 'pcap' && ext !== 'pcapng') {
            alert('只支持PCAP和PCAPNG文件');
            return;
        }

        // 更新系统状态
        window.updateSystemStatus('分析中...', 'warning');

        // 显示文件信息
        const fileNameElement = document.getElementById('file-name');
        const fileSizeElement = document.getElementById('file-size');
        const fileModifiedElement = document.getElementById('file-modified');
        const packetCountElement = document.getElementById('packet-count');

        if (fileNameElement) fileNameElement.textContent = file.name;
        if (fileSizeElement) fileSizeElement.textContent = window.formatFileSize(file.size);
        if (fileModifiedElement) fileModifiedElement.textContent = new Date(file.lastModified).toLocaleString();
        if (packetCountElement) packetCountElement.textContent = '计算中...';

        // 更新分析状态
        const analysisStatusElement = document.getElementById('analysis-status');
        if (analysisStatusElement) {
            analysisStatusElement.textContent = '分析中';
            analysisStatusElement.className = 'status-badge bg-warning';
        }

        // 创建FormData对象并发送文件
        const formData = new FormData();
        formData.append('file', file);

        // 发送分析请求
        fetch('/start-analysis', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'error') {
                alert(data.message);
                window.updateSystemStatus('就绪', 'success');
                return;
            }

            // 设置分析ID
            window.currentAnalysisId = data.analysis_id;

            // 开始轮询分析状态
            pollAnalysisStatus();
        })
        .catch(error => {
            console.error('分析请求失败:', error);
            alert('分析请求失败，请重试');
            window.updateSystemStatus('就绪', 'success');
        });
    }

    // 轮询分析状态
    async function pollAnalysisStatus() {
        if (!window.currentAnalysisId) return;

        try {
            const response = await fetch(`/analysis/${window.currentAnalysisId}/status`);
            const data = await response.json();

            if (data.status === 'completed') {
                // 分析完成
                const analysisStatusElement = document.getElementById('analysis-status');
                const packetCountElement = document.getElementById('packet-count');

                if (analysisStatusElement) {
                    analysisStatusElement.textContent = '已完成';
                    analysisStatusElement.className = 'status-badge bg-success';
                }

                if (packetCountElement) {
                    packetCountElement.textContent = data.packet_count; // 实际应从API获取
                }

                window.updateSystemStatus('就绪', 'success');

            } else if (data.status === 'failed') {
                // 分析失败
                const analysisStatusElement = document.getElementById('analysis-status');
                if (analysisStatusElement) {
                    analysisStatusElement.textContent = '失败';
                    analysisStatusElement.className = 'status-badge bg-danger';
                }
                window.updateSystemStatus('分析失败', 'danger');

            } else {
                // 分析中，继续轮询
                setTimeout(pollAnalysisStatus, 2000);
            }
        } catch (error) {
            console.error('获取分析状态失败:', error);
            setTimeout(pollAnalysisStatus, 2000);
        }
    }
}