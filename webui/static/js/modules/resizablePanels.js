// 可调整大小面板模块
export function setupResizablePanels() {
    const resizers = document.querySelectorAll('.panel-resizer');
    let isResizing = false;
    let currentResizer = null;
    let startX, startY, startWidth, startHeight;

    resizers.forEach(resizer => {
        resizer.addEventListener('mousedown', initResize);
    });

    document.addEventListener('mousemove', resize);
    document.addEventListener('mouseup', stopResize);

    // 设置折叠按钮事件
    setupCollapseButtons();

    function initResize(e) {
        isResizing = true;
        currentResizer = e.target;

        const panelId = currentResizer.getAttribute('data-panel');
        const panel = document.getElementById(panelId);

        if (!panel) return;

        if (currentResizer.classList.contains('horizontal-resizer')) {
            // 水平调整（上下面板）
            startY = e.clientY;
            startHeight = parseInt(document.defaultView.getComputedStyle(panel).height, 10);
        } else if (currentResizer.classList.contains('vertical-resizer')) {
            // 垂直调整（左右面板）
            startX = e.clientX;
            startWidth = parseInt(document.defaultView.getComputedStyle(panel).width, 10);
        }

        e.preventDefault();
    }

    function resize(e) {
        if (!isResizing || !currentResizer) return;

        const panelId = currentResizer.getAttribute('data-panel');
        const panel = document.getElementById(panelId);

        if (!panel) return;

        // 边界常量
        const MIN_TOP_HEIGHT = 100;
        const MAX_TOP_HEIGHT = window.innerHeight * 0.7;
        const MIN_LEFT_WIDTH = 150;
        const MAX_LEFT_WIDTH = window.innerWidth * 0.5;

        if (currentResizer.classList.contains('horizontal-resizer')) {
            // 调整上下面板高度
            const dy = e.clientY - startY;
            let newHeight = startHeight + dy;

            // 边界检查
            if (newHeight < MIN_TOP_HEIGHT) {
                newHeight = MIN_TOP_HEIGHT;
                showBoundary('top');
            } else if (newHeight > MAX_TOP_HEIGHT) {
                newHeight = MAX_TOP_HEIGHT;
                showBoundary('top');
            } else {
                hideBoundary('top');
            }

            // 设置新高度
            panel.style.height = newHeight + 'px';

        } else if (currentResizer.classList.contains('vertical-resizer')) {
            // 调整左右面板宽度
            const dx = e.clientX - startX;
            let newWidth = startWidth + dx;

            // 边界检查
            if (newWidth < MIN_LEFT_WIDTH) {
                newWidth = MIN_LEFT_WIDTH;
                showBoundary('left');
            } else if (newWidth > MAX_LEFT_WIDTH) {
                newWidth = MAX_LEFT_WIDTH;
                showBoundary('left');
            } else {
                hideBoundary('left');
            }

            // 设置新宽度
            panel.style.width = newWidth + 'px';
        }
    }

    function stopResize() {
        isResizing = false;
        currentResizer = null;

        // 隐藏所有边界指示器
        document.querySelectorAll('.resize-boundary').forEach(boundary => {
            boundary.style.display = 'none';
        });

        // 移除所有边界标记
        document.querySelectorAll('.panel-resizer').forEach(resizer => {
            resizer.classList.remove('at-boundary');
        });
    }

    // 显示边界指示器
    function showBoundary(type) {
        const boundary = document.getElementById(`${type}-boundary`);
        if (boundary) {
            boundary.style.display = 'block';
        }

        // 标记调整手柄在边界
        const resizers = document.querySelectorAll('.panel-resizer');
        resizers.forEach(resizer => {
            if (resizer.getAttribute('data-panel').includes(type)) {
                resizer.classList.add('at-boundary');
            }
        });
    }

    // 隐藏边界指示器
    function hideBoundary(type) {
        const boundary = document.getElementById(`${type}-boundary`);
        if (boundary) {
            boundary.style.display = 'none';
        }

        // 移除调整手柄的边界标记
        const resizers = document.querySelectorAll('.panel-resizer');
        resizers.forEach(resizer => {
            if (resizer.getAttribute('data-panel').includes(type)) {
                resizer.classList.remove('at-boundary');
            }
        });
    }

    // 设置折叠按钮事件
    function setupCollapseButtons() {
        // 顶部折叠按钮
        const collapseTopBtn = document.getElementById('collapse-top-btn');
        if (collapseTopBtn) {
            collapseTopBtn.addEventListener('click', function() {
                const topPanel = document.getElementById('top-panel');
                if (topPanel.classList.contains('collapsed')) {
                    // 展开顶部面板
                    topPanel.classList.remove('collapsed');
                    this.querySelector('i').className = 'bi bi-chevron-up';
                    // 恢复默认高度
                    topPanel.style.height = '200px';
                } else {
                    // 折叠顶部面板
                    topPanel.classList.add('collapsed');
                    this.querySelector('i').className = 'bi bi-chevron-down';
                }
            });
        }

        // 左侧折叠按钮
        const collapseLeftBtn = document.getElementById('collapse-left-btn');
        if (collapseLeftBtn) {
            collapseLeftBtn.addEventListener('click', function() {
                const leftTabs = document.getElementById('left-tabs');
                if (leftTabs.classList.contains('collapsed')) {
                    // 展开左侧面板
                    leftTabs.classList.remove('collapsed');
                    this.querySelector('i').className = 'bi bi-chevron-left';
                    // 恢复默认宽度
                    leftTabs.style.width = '250px';
                } else {
                    // 折叠左侧面板
                    leftTabs.classList.add('collapsed');
                    this.querySelector('i').className = 'bi bi-chevron-right';
                }
            });
        }
    }
}