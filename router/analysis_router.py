from flask import Flask, render_template, request, jsonify
import os
import uuid
import threading
import time
import logging
from werkzeug.utils import secure_filename
from analysis import load_analyzers
from parser.pcap_parser import PcapParser
from router.base_router import base_router
from storage.database import RedisManager
from storage.cache import AnalysisCache
import humanize


def analysis_router(App):
    @App.app.route('/analysis/<analysis_id>/status')
    def get_analysis_status(analysis_id):
        """获取分析状态"""
        status = App.cache.get(f"analysis:{analysis_id}:status") or "unknown"
        packet_count = App.cache.get(f"analysis:{analysis_id}:packet_count") or 0
        return jsonify({
            'status': status,
            'packet_count': packet_count
        })

    @App.app.route('/analysis/<analysis_id>/protocol-stats')
    def get_protocol_stats(analysis_id):
        """获取协议统计结果"""
        # 从数据库获取结果
        results = App.redis_manager.get_results(analysis_id, "ProtocolStatsAnalyzer")
        # print(123)
        print(results)
        if results:
            return jsonify(results)
        return jsonify({'protocol_distribution': []})

    @App.app.route('/analysis/<analysis_id>/sql-detections')
    def get_sql_detections(analysis_id):
        """获取SQL注入检测结果"""
        # 从数据库获取结果
        results = App.redis_manager.get_results(analysis_id, "SQLInjectionAnalyzer")
        if results:
            return jsonify(results)
        return jsonify({'detections': []})

    @App.app.route('/analysis/<analysis_id>/extracted-files')
    def get_extracted_files(analysis_id):
        """获取提取的文件列表"""
        # 从数据库获取结果
        results = App.redis_manager.get_results(analysis_id, "FileExtractor")
        if results:
            return jsonify(results)
        return jsonify({'files': []})

    @App.app.route('/analysis/<analysis_id>/results')
    def get_all_results(analysis_id):
        """获取所有分析结果"""
        # 从缓存获取结果
        results = App.cache.get(f"analysis:{analysis_id}:results")
        if results:
            return jsonify(results)

        # 如果缓存中没有，从数据库获取
        all_results = {}
        for analyzer in App.analyzers:
            analyzer_results = App.redis_manager.get_results(analysis_id, analyzer.name)
            if analyzer_results:
                all_results[analyzer.name] = analyzer_results

        return jsonify(all_results)
