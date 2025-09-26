from flask import render_template, jsonify, request
from storage.database import DatabaseManager
from storage.cache import AnalysisCache


def init_routes(app):
    db_manager = DatabaseManager()
    cache = AnalysisCache()

    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/api/protocol-stats')
    def protocol_stats():
        # 尝试从缓存获取
        cached = cache.get('protocol_stats')
        if cached:
            return jsonify(cached)

        # 从数据库获取
        results = db_manager.get_analysis_results('ProtocolStatsAnalyzer', limit=1)
        if results:
            data = results[0]
            cache.set('protocol_stats', data)
            return jsonify(data)
        return jsonify({})

    @app.route('/threats/sql-injection')
    def sql_injection_view():
        results = db_manager.get_analysis_results('SQLInjectionAnalyzer', limit=100)
        return render_template('threats/sql_injection.html', detections=results)

    # 添加更多路由...