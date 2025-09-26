// 主入口文件
import { setupFileHandling } from './modules/fileHandler.js';
import { setupResizablePanels } from './modules/resizablePanels.js';
import { setupProtocolStats } from './modules/protocolStats.js';
import { setupSqlInjection } from './modules/sqlInjection.js';
import { setupFileExtraction } from './modules/fileExtraction.js';
import { setupTrafficAnalysis } from './modules/trafficAnalysis.js';
import { setupCustomAnalysis } from './modules/customAnalysis.js';

// 全局状态
let currentAnalysisId = null;

// 初始化函数
function initialize() {
    // 设置文件处理
    setupFileHandling();

    // 设置可调整大小的面板
    setupResizablePanels();

    // 设置各分析模块
    setupProtocolStats();
    setupSqlInjection();
    setupFileExtraction();
    setupTrafficAnalysis();
    setupCustomAnalysis();

    // 初始化时钟
    updateClock();
    setInterval(updateClock, 1000);
}

// 更新时间显示
function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        timeElement.textContent = timeStr;
    }
}

// 更新系统状态
function updateSystemStatus(status, type = 'success') {
    const statusElement = document.getElementById('system-status');
    if (!statusElement) return;

    statusElement.textContent = status;

    // 移除所有状态类
    statusElement.parentElement.classList.remove('text-success', 'text-warning', 'text-danger');

    // 添加新状态类
    if (type === 'success') {
        statusElement.parentElement.classList.add('text-success');
    } else if (type === 'warning') {
        statusElement.parentElement.classList.add('text-warning');
    } else if (type === 'danger') {
        statusElement.parentElement.classList.add('text-danger');
    }
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 导出全局函数
window.updateSystemStatus = updateSystemStatus;
window.formatFileSize = formatFileSize;
window.currentAnalysisId = currentAnalysisId;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initialize);