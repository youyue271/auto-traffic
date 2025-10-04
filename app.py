from flask import Flask, render_template, request, jsonify
import os
import uuid
import threading
import time
import logging
from werkzeug.utils import secure_filename
from analysis import load_analyzers
from parser.pcap_parser import PcapParser
from router.analysis_router import analysis_router
from router.base_router import base_router
from storage.database import RedisManager
from storage.cache import AnalysisCache
import humanize


class App:
    def __init__(self, config_path="./config.py"):

        self.app = Flask(__name__)
        self.app.config.from_pyfile(config_path)

        # 确保上传目录存在
        UPLOAD_FOLDER = 'uploads'
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        self.app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        # 初始化数据库和缓存
        self.redis_manager = RedisManager(self.app.config['REDIS_URL'])
        self.cache = AnalysisCache(self.redis_manager.connection, maxsize=1000, ttl=300)

        # 加载分析器
        self.analyzers = load_analyzers()
        print(self.analyzers)

        # 加载router
        base_router(self)
        analysis_router(self)




def log():
    log_dir = 'log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('log/app.log'),
            logging.StreamHandler()
        ]
    )


if __name__ == '__main__':
    # 配置日志
    log()

    # 创建应用
    App = App()
    App.app.run(
        host=App.app.config.get('WEB_HOST', '0.0.0.0'),
        port=App.app.config.get('WEB_PORT', 5000),
        debug=App.app.config.get('DEBUG', False)
    )

