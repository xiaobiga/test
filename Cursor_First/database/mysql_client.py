import pymysql
from typing import Optional, List, Dict, Any
from loguru import logger
from config import Config

class MySQLClient:
    """MySQL数据库客户端"""
    
    def __init__(self):
        self.config = Config()
        self.connection = None
        self._connect()
        self._init_tables()
    
    def _connect(self):
        """连接MySQL数据库"""
        try:
            self.connection = pymysql.connect(
                host=self.config.MYSQL_HOST,
                port=self.config.MYSQL_PORT,
                user=self.config.MYSQL_USER,
                password=self.config.MYSQL_PASSWORD,
                database=self.config.MYSQL_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("MySQL数据库连接成功")
        except Exception as e:
            logger.error(f"MySQL数据库连接失败: {e}")
            raise
    
    def _init_tables(self):
        """初始化数据表"""
        try:
            with self.connection.cursor() as cursor:
                # 创建问答表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS qa_pairs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        category VARCHAR(100),
                        confidence FLOAT DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_question (question(255)),
                        INDEX idx_category (category),
                        INDEX idx_confidence (confidence)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # 创建用户查询日志表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS query_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(100),
                        query TEXT NOT NULL,
                        response TEXT,
                        source VARCHAR(50),
                        response_time FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_user_id (user_id),
                        INDEX idx_created_at (created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # 创建文档表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        doc_id VARCHAR(100) UNIQUE NOT NULL,
                        title VARCHAR(500),
                        content TEXT,
                        category VARCHAR(100),
                        parent_id VARCHAR(100),
                        child_id VARCHAR(100),
                        embedding_vector LONGTEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_doc_id (doc_id),
                        INDEX idx_category (category),
                        INDEX idx_parent_id (parent_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
            self.connection.commit()
            logger.info("数据表初始化完成")
        except Exception as e:
            logger.error(f"数据表初始化失败: {e}")
            raise
    
    def search_qa(self, question: str, threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """搜索问答对"""
        try:
            with self.connection.cursor() as cursor:
                # 使用简单的关键词匹配，实际项目中可以使用更复杂的相似度算法
                cursor.execute("""
                    SELECT * FROM qa_pairs 
                    WHERE MATCH(question) AGAINST(%s IN NATURAL LANGUAGE MODE)
                    AND confidence >= %s
                    ORDER BY confidence DESC, updated_at DESC
                    LIMIT 1
                """, (question, threshold))
                
                result = cursor.fetchone()
                return result
        except Exception as e:
            logger.error(f"搜索问答对失败: {e}")
            return None
    
    def insert_qa(self, question: str, answer: str, category: str = None, confidence: float = 1.0) -> bool:
        """插入新的问答对"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO qa_pairs (question, answer, category, confidence)
                    VALUES (%s, %s, %s, %s)
                """, (question, answer, category, confidence))
                
            self.connection.commit()
            logger.info(f"插入问答对成功: {question[:50]}...")
            return True
        except Exception as e:
            logger.error(f"插入问答对失败: {e}")
            return False
    
    def log_query(self, user_id: str, query: str, response: str, source: str, response_time: float) -> bool:
        """记录用户查询日志"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO query_logs (user_id, query, response, source, response_time)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, query, response, source, response_time))
                
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"记录查询日志失败: {e}")
            return False
    
    def get_qa_statistics(self) -> Dict[str, Any]:
        """获取问答统计信息"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as total FROM qa_pairs")
                total = cursor.fetchone()['total']
                
                cursor.execute("SELECT COUNT(*) as high_conf FROM qa_pairs WHERE confidence >= 0.8")
                high_conf = cursor.fetchone()['high_conf']
                
                cursor.execute("SELECT COUNT(*) as today FROM qa_pairs WHERE DATE(created_at) = CURDATE()")
                today = cursor.fetchone()['today']
                
                return {
                    "total_qa": total,
                    "high_confidence": high_conf,
                    "today_added": today
                }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("MySQL数据库连接已关闭")


