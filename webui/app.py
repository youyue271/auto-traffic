from flask import Flask, render_template, request, jsonify
import os
import uuid
import threading
import time
import logging
from werkzeug.utils import secure_filename
from analysis import load_analyzers
from parser.pcap_parser import PcapParser
from storage.database import DatabaseManager
from storage.cache import AnalysisCache

app = Flask(__name__)
app.config.from_pyfile('../config.py')

# 确保上传目录存在
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 初始化数据库和缓存
db_manager = DatabaseManager(app.config['DATABASE_URI'])
cache = AnalysisCache(maxsize=1000, ttl=300)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start-analysis', methods=['POST'])
def start_analysis():
    """开始分析上传的文件"""
    # 检查是否有文件被上传
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': '没有选择文件'}), 400

    file = request.files['file']

    # 如果用户没有选择文件
    if file.filename == '':
        return jsonify({'status': 'error', 'message': '请选择一个文件'}), 400

    # 验证文件类型
    if not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': '不支持的文件类型'}), 400

    try:
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        filename = secure_filename(f"{file_id}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # 保存文件
        file.save(filepath)

        # 生成分析ID
        analysis_id = str(uuid.uuid4())

        # 启动分析任务
        threading.Thread(target=perform_analysis, args=(analysis_id, filepath)).start()

        # 返回文件基本信息
        file_info = {
            'filename': file.filename,
            'size': format_file_size(os.path.getsize(filepath)),
            'modified': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(filepath)))
        }

        return jsonify({
            'status': 'success',
            'analysis_id': analysis_id,
            'file_info': file_info
        })

    except Exception as e:
        logging.error(f"文件处理失败: {str(e)}")
        return jsonify({'status': 'error', 'message': '文件处理失败'}), 500


def allowed_file(filename):
    """检查文件扩展名是否合法"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'pcap', 'pcapng'}


def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {size_names[i]}"


def perform_analysis(analysis_id, filepath):
    """执行分析任务"""
    try:
        # 在缓存中标记分析开始
        cache.set(f"analysis:{analysis_id}:status", "processing")
        cache.set(f"analysis:{analysis_id}:filepath", filepath)

        # 初始化解析器
        parser = PcapParser(filepath)

        # 加载分析器
        analyzers = load_analyzers()

        # 解析并分析每个数据包
        for packet in parser.parse():
            for analyzer in analyzers:
                analyzer.analyze(packet)

        # 完成分析
        for analyzer in analyzers:
            analyzer.finalize()
            results = analyzer.get_results()

            # 存储结果
            db_manager.save_results(
                analysis_id=analysis_id,
                analyzer_name=analyzer.__class__.__name__,
                results=results
            )

        # 更新状态
        cache.set(f"analysis:{analysis_id}:status", "completed")
        cache.set(f"analysis:{analysis_id}:completed_at", time.time())

    except Exception as e:
        cache.set(f"analysis:{analysis_id}:status", "failed")
        cache.set(f"analysis:{analysis_id}:error", str(e))


@app.route('/analysis/<analysis_id>/status')
def get_analysis_status(analysis_id):
    """获取分析状态"""
    status = cache.get(f"analysis:{analysis_id}:status") or "unknown"
    return jsonify({'status': status})


@app.route('/analysis/<analysis_id>/protocol-stats')
def get_protocol_stats(analysis_id):
    """获取协议统计结果"""
    results = db_manager.get_results(analysis_id, "ProtocolStatsAnalyzer")
    if results:
        return jsonify(results[0])
    return jsonify({'protocol_distribution': []})


@app.route('/analysis/<analysis_id>/sql-detections')
def get_sql_detections(analysis_id):
    """获取SQL注入检测结果"""
    results = db_manager.get_results(analysis_id, "SQLInjectionAnalyzer")
    if results:
        return jsonify(results[0])
    return jsonify({'detections': []})


@app.route('/analysis/<analysis_id>/extracted-files')
def get_extracted_files(analysis_id):
    """获取提取的文件列表"""
    results = db_manager.get_results(analysis_id, "FileExtractor")
    if results:
        return jsonify(results[0])
    return jsonify({'files': []})


if __name__ == '__main__':
    app.run(host=app.config['WEB_HOST'], port=app.config['WEB_PORT'])