#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库、表和初始数据
"""

import os
import sys
import pymysql
from loguru import logger

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def init_database():
    """初始化数据库"""
    config = Config()
    
    try:
        # 连接MySQL（不指定数据库）
        connection = pymysql.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info(f"数据库 {config.MYSQL_DATABASE} 创建成功")
            
            # 使用数据库
            cursor.execute(f"USE {config.MYSQL_DATABASE}")
            
            # 创建表
            _create_tables(cursor)
            
            # 插入初始数据
            _insert_initial_data(cursor)
            
        connection.commit()
        logger.info("数据库初始化完成")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    finally:
        if connection:
            connection.close()

def _create_tables(cursor):
    """创建数据表"""
    try:
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
        
        # 创建系统配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id INT AUTO_INCREMENT PRIMARY KEY,
                config_key VARCHAR(100) UNIQUE NOT NULL,
                config_value TEXT,
                description VARCHAR(500),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        logger.info("数据表创建完成")
        
    except Exception as e:
        logger.error(f"创建表失败: {e}")
        raise

def _insert_initial_data(cursor):
    """插入初始数据"""
    try:
        # 插入示例问答对
        sample_qa = [
            ("篮球鞋怎么选择？", "选择篮球鞋时需要考虑以下几个方面：\n1. 脚型：高脚背选择高帮，低脚背选择低帮\n2. 场地：室内选择橡胶底，室外选择耐磨底\n3. 位置：后卫选择轻便型，中锋选择支撑型\n4. 品牌：耐克、阿迪达斯、李宁等都是不错的选择", "篮球装备"),
            ("护膝怎么戴？", "护膝的正确佩戴方法：\n1. 选择合适尺寸的护膝\n2. 将护膝套在膝盖上，确保髌骨在护膝中央\n3. 调整松紧度，既不能太松也不能太紧\n4. 运动时保持护膝位置稳定", "防护装备"),
            ("跑步机怎么使用？", "跑步机使用步骤：\n1. 开机前检查安全锁是否扣好\n2. 选择合适的速度和坡度\n3. 先慢走热身，再逐渐加速\n4. 结束时逐渐减速，不要突然停止\n5. 注意保持正确姿势", "健身器材"),
            ("瑜伽垫怎么选择？", "瑜伽垫选择要点：\n1. 厚度：初学者选择6-8mm，进阶者选择3-5mm\n2. 材质：TPE环保材质，无毒无味\n3. 防滑性：表面要有防滑纹理\n4. 尺寸：根据身高选择合适长度", "瑜伽用品"),
            ("哑铃重量怎么选择？", "哑铃重量选择原则：\n1. 男性初学者：5-10kg\n2. 女性初学者：2-5kg\n3. 根据训练目标调整：增肌选择较重，塑形选择较轻\n4. 循序渐进，逐步增加重量", "健身器材")
        ]
        
        for question, answer, category in sample_qa:
            cursor.execute("""
                INSERT IGNORE INTO qa_pairs (question, answer, category, confidence)
                VALUES (%s, %s, %s, %s)
            """, (question, answer, category, 0.9))
        
        # 插入系统配置
        system_configs = [
            ("system_version", "1.0.0", "系统版本号"),
            ("max_query_length", "1000", "最大查询长度"),
            ("cache_expire_time", "3600", "缓存过期时间（秒）"),
            ("vector_search_top_k", "10", "向量搜索返回数量"),
            ("llm_model", "gpt-3.5-turbo", "大语言模型名称")
        ]
        
        for key, value, description in system_configs:
            cursor.execute("""
                INSERT IGNORE INTO system_config (config_key, config_value, description)
                VALUES (%s, %s, %s)
            """, (key, value, description))
        
        logger.info("初始数据插入完成")
        
    except Exception as e:
        logger.error(f"插入初始数据失败: {e}")
        raise

def create_sample_documents():
    """创建示例文档数据"""
    try:
        # 这里可以添加更多示例文档
        sample_docs = [
            {
                "title": "篮球鞋选购指南",
                "content": "篮球鞋是篮球运动的重要装备，选择合适的篮球鞋对运动表现和脚部健康都很重要。\n\n选择篮球鞋时，首先要考虑脚型。高脚背的人适合选择高帮篮球鞋，能够提供更好的脚踝支撑。低脚背的人可以选择低帮篮球鞋，更加灵活轻便。\n\n其次要考虑场地类型。室内篮球场建议选择橡胶底的篮球鞋，防滑性能更好。室外篮球场建议选择耐磨底的篮球鞋，使用寿命更长。\n\n最后要考虑场上位置。后卫球员需要快速移动和变向，建议选择轻便型的篮球鞋。中锋球员需要在内线对抗，建议选择支撑型的篮球鞋。",
                "category": "篮球装备"
            },
            {
                "title": "护膝使用说明",
                "content": "护膝是运动防护的重要装备，正确使用护膝可以有效预防运动损伤。\n\n护膝的主要作用是保护膝关节，减少运动时的冲击和摩擦。选择合适的护膝尺寸很重要，太松起不到保护作用，太紧会影响血液循环。\n\n佩戴护膝时，要确保髌骨在护膝的中央位置，这样能够提供最佳的支撑和保护。运动过程中要经常检查护膝位置，确保没有移位。\n\n护膝的清洗也很重要，建议使用温和的洗涤剂手洗，避免机洗和漂白。晾干时要避免阳光直射，防止材质老化。",
                "category": "防护装备"
            }
        ]
        
        logger.info(f"创建了{len(sample_docs)}个示例文档")
        return sample_docs
        
    except Exception as e:
        logger.error(f"创建示例文档失败: {e}")
        return []

if __name__ == "__main__":
    try:
        logger.info("开始初始化数据库...")
        init_database()
        logger.info("数据库初始化成功！")
        
        # 创建示例文档
        sample_docs = create_sample_documents()
        logger.info(f"示例文档创建完成，共{len(sample_docs)}个")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        sys.exit(1)


