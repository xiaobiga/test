import redis
import json
import pickle
from typing import Optional, Any, Dict
from loguru import logger
from config import Config

class RedisClient:
    """Redis缓存客户端"""
    
    def __init__(self):
        self.config = Config()
        self.client = None
        self._connect()
    
    def _connect(self):
        """连接Redis数据库"""
        try:
            self.client = redis.Redis(
                host=self.config.REDIS_HOST,
                port=self.config.REDIS_PORT,
                db=self.config.REDIS_DB,
                password=self.config.REDIS_PASSWORD,
                decode_responses=False,  # 保持二进制格式以支持pickle
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 测试连接
            self.client.ping()
            logger.info("Redis数据库连接成功")
        except Exception as e:
            logger.error(f"Redis数据库连接失败: {e}")
            raise
    
    def set_cache(self, key: str, value: Any, expire: int = None) -> bool:
        """设置缓存"""
        try:
            if expire is None:
                expire = self.config.CACHE_EXPIRE_TIME
            
            # 使用pickle序列化复杂对象
            serialized_value = pickle.dumps(value)
            result = self.client.setex(key, expire, serialized_value)
            return result
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = self.client.get(key)
            if value is None:
                return None
            
            # 反序列化
            return pickle.loads(value)
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return False
    
    def delete_cache(self, key: str) -> bool:
        """删除缓存"""
        try:
            result = self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    def exists_cache(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"检查缓存失败: {e}")
            return False
    
    def set_qa_cache(self, question: str, answer: str, category: str = None) -> bool:
        """缓存问答对"""
        try:
            cache_key = f"qa:{hash(question)}"
            cache_value = {
                "question": question,
                "answer": answer,
                "category": category,
                "timestamp": self.client.time()[0]
            }
            return self.set_cache(cache_key, cache_value)
        except Exception as e:
            logger.error(f"缓存问答对失败: {e}")
            return False
    
    def get_qa_cache(self, question: str) -> Optional[Dict]:
        """获取缓存的问答对"""
        try:
            cache_key = f"qa:{hash(question)}"
            return self.get_cache(cache_key)
        except Exception as e:
            logger.error(f"获取问答缓存失败: {e}")
            return None
    
    def increment_query_count(self, question: str) -> int:
        """增加查询计数"""
        try:
            count_key = f"count:{hash(question)}"
            return self.client.incr(count_key)
        except Exception as e:
            logger.error(f"增加查询计数失败: {e}")
            return 0
    
    def get_query_count(self, question: str) -> int:
        """获取查询计数"""
        try:
            count_key = f"count:{hash(question)}"
            count = self.client.get(count_key)
            return int(count) if count else 0
        except Exception as e:
            logger.error(f"获取查询计数失败: {e}")
            return 0
    
    def get_hot_queries(self, limit: int = 10) -> list:
        """获取热门查询"""
        try:
            pattern = "count:*"
            keys = self.client.keys(pattern)
            hot_queries = []
            
            for key in keys:
                count = int(self.client.get(key))
                hot_queries.append((key.decode(), count))
            
            # 按计数排序
            hot_queries.sort(key=lambda x: x[1], reverse=True)
            return hot_queries[:limit]
        except Exception as e:
            logger.error(f"获取热门查询失败: {e}")
            return []
    
    def clear_expired_cache(self) -> int:
        """清理过期缓存"""
        try:
            # Redis会自动清理过期键，这里只是统计
            return 0
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            info = self.client.info()
            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {}
    
    def close(self):
        """关闭Redis连接"""
        if self.client:
            self.client.close()
            logger.info("Redis数据库连接已关闭")


