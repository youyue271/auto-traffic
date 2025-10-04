class AnalysisCache:
    def __init__(self, redis_connection, maxsize=1000, ttl=300):
        self.redis = redis_connection
        self.maxsize = maxsize
        self.ttl = ttl  # 秒

    def set(self, key, value):
        """设置缓存值"""
        if isinstance(value, (int, float)):
            self.redis.set(key, value, ex=self.ttl)
        else:
            self.redis.set(key, str(value), ex=self.ttl)

    def get(self, key):
        """获取缓存值"""
        value = self.redis.get(key)
        if value is None:
            return None

        # 尝试转换类型
        try:
            return int(value)
        except (ValueError, TypeError):
            try:
                return float(value)
            except (ValueError, TypeError):
                return value.decode('utf-8') if isinstance(value, bytes) else value