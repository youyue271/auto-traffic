import redis
import json


class RedisManager:
    def __init__(self, redis_url):
        self.connection = redis.Redis.from_url(redis_url, decode_responses=True)

    def save_results(self, analysis_id, analyzer_name, results):
        """保存分析结果到Redis"""
        key = f"analysis:{analysis_id}:{analyzer_name}"
        self.connection.set(key, json.dumps(results))
        # 设置过期时间（24小时）
        self.connection.expire(key, 24 * 60 * 60)

    def get_results(self, analysis_id, analyzer_name):
        """从Redis获取分析结果"""
        key = f"analysis:{analysis_id}:{analyzer_name}"
        results_json = self.connection.get(key)
        if results_json:
            return json.loads(results_json)
        return None