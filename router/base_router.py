from flask import Flask, render_template, request, jsonify
import os
import uuid
import threading
import time
import logging
from werkzeug.utils import secure_filename
from analysis import load_analyzers
from config import ALLOWED_EXTENSIONS
from parser.pcap_parser import PcapParser
from storage.database import RedisManager
from storage.cache import AnalysisCache
import humanize


def base_router(App):
    def allowed_file(filename):
        """检查文件扩展名是否合法"""
        return '.' in filename and \
            filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS

    def format_file_size(size_bytes):
        """格式化文件大小"""
        return humanize.naturalsize(size_bytes)

    def perform_analysis(analysis_id, filepath):
        """执行分析任务"""
        try:
            # 在缓存中标记分析开始
            App.cache.set(f"analysis:{analysis_id}:status", "processing")
            App.cache.set(f"analysis:{analysis_id}:filepath", filepath)
            # print(123)
            # 初始化解析器
            parser = PcapParser(filepath)
            # print(234)
            # 解析并分析每个数据包
            packet_count = 0
            for packet in parser.parse():
                packet_count += 1
                for analyzer in App.analyzers:
                    analyzer.analyze(packet)

                # 每100个包更新一次进度
                if packet_count % 100 == 0:
                    App.cache.set(f"analysis:{analysis_id}:packet_count", packet_count)

                # print(packet_count)
            # 完成分析
            results = {}
            for analyzer in App.analyzers:
                analyzer.finalize()
                analyzer_results = analyzer.get_results()
                results[analyzer.name] = analyzer_results

                # 存储结果
                App.redis_manager.save_results(
                    analysis_id=analysis_id,
                    analyzer_name=analyzer.name,
                    results=analyzer_results
                )

            # 更新状态
            App.cache.set(f"analysis:{analysis_id}:status", "completed")
            App.cache.set(f"analysis:{analysis_id}:completed_at", time.time())
            App.cache.set(f"analysis:{analysis_id}:packet_count", packet_count)
            App.cache.set(f"analysis:{analysis_id}:results", results)

        except Exception as e:
            logging.error(f"分析失败: {str(e)}")
            App.cache.set(f"analysis:{analysis_id}:status", "failed")
            App.cache.set(f"analysis:{analysis_id}:error", str(e))

    @App.app.route('/')
    def index():
        return render_template('index.html')

    @App.app.route('/start-analysis', methods=['POST'])
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
            filepath = os.path.join(App.app.config['UPLOAD_FOLDER'], filename)

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
