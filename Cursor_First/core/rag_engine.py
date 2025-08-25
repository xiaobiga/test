import time
from typing import Dict, List, Any, Optional
from loguru import logger

from database.mysql_client import MySQLClient
from database.redis_client import RedisClient
from models.intent_classifier import IntentClassifierManager
from models.query_optimizer import QueryOptimizer
from vector_store.milvus_client import MilvusClient
from models.embedding_model import EmbeddingManager
from llm.openai_client import LLMManager

class RAGEngine:
    """RAG引擎核心模块"""
    
    def __init__(self):
        self.config = Config()
        
        # 初始化各个组件
        self.mysql_client = None
        self.redis_client = None
        self.intent_classifier = None
        self.query_optimizer = None
        self.milvus_client = None
        self.embedding_manager = None
        self.llm_manager = None
        
        self._init_components()
        logger.info("RAG引擎初始化完成")
    
    def _init_components(self):
        """初始化各个组件"""
        try:
            # 初始化数据库客户端
            self.mysql_client = MySQLClient()
            self.redis_client = RedisClient()
            
            # 初始化AI模型
            self.intent_classifier = IntentClassifierManager()
            self.query_optimizer = QueryOptimizer()
            self.embedding_manager = EmbeddingManager()
            self.llm_manager = LLMManager()
            
            # 初始化向量数据库
            self.milvus_client = MilvusClient()
            
            logger.info("所有组件初始化成功")
            
        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            raise
    
    def process_query(self, 
                     query: str, 
                     user_id: str = None,
                     session_id: str = None) -> Dict[str, Any]:
        """处理用户查询的主流程"""
        start_time = time.time()
        
        try:
            logger.info(f"开始处理查询: {query[:100]}...")
            
            # 1. 检查Redis缓存
            cached_response = self._check_cache(query)
            if cached_response:
                logger.info("从缓存获取回复")
                return self._build_response(
                    query=query,
                    reply=cached_response["answer"],
                    source="cache",
                    response_time=time.time() - start_time,
                    user_id=user_id,
                    session_id=session_id
                )
            
            # 2. 检查MySQL数据库
            mysql_response = self._check_mysql(query)
            if mysql_response:
                logger.info("从MySQL获取回复")
                # 缓存到Redis
                self._cache_response(query, mysql_response["answer"])
                return self._build_response(
                    query=query,
                    reply=mysql_response["answer"],
                    source="mysql",
                    response_time=time.time() - start_time,
                    user_id=user_id,
                    session_id=session_id
                )
            
            # 3. 进入RAG系统
            logger.info("进入RAG系统处理")
            rag_response = self._process_with_rag(query)
            
            # 4. 记录查询日志
            self._log_query(user_id, query, rag_response["reply"], "rag", time.time() - start_time)
            
            return self._build_response(
                query=query,
                reply=rag_response["reply"],
                source="rag",
                response_time=time.time() - start_time,
                user_id=user_id,
                session_id=session_id,
                rag_details=rag_response
            )
            
        except Exception as e:
            logger.error(f"查询处理失败: {e}")
            error_response = f"抱歉，处理您的查询时出现错误，请稍后重试或联系人工客服。错误信息：{str(e)}"
            
            # 记录错误日志
            self._log_query(user_id, query, error_response, "error", time.time() - start_time)
            
            return self._build_response(
                query=query,
                reply=error_response,
                source="error",
                response_time=time.time() - start_time,
                user_id=user_id,
                session_id=session_id,
                error=str(e)
            )
    
    def _check_cache(self, query: str) -> Optional[Dict[str, Any]]:
        """检查Redis缓存"""
        try:
            return self.redis_client.get_qa_cache(query)
        except Exception as e:
            logger.error(f"缓存检查失败: {e}")
            return None
    
    def _check_mysql(self, query: str) -> Optional[Dict[str, Any]]:
        """检查MySQL数据库"""
        try:
            return self.mysql_client.search_qa(query)
        except Exception as e:
            logger.error(f"MySQL查询失败: {e}")
            return None
    
    def _cache_response(self, query: str, answer: str):
        """缓存回复到Redis"""
        try:
            self.redis_client.set_qa_cache(query, answer)
            # 增加查询计数
            self.redis_client.increment_query_count(query)
        except Exception as e:
            logger.error(f"缓存回复失败: {e}")
    
    def _process_with_rag(self, query: str) -> Dict[str, Any]:
        """使用RAG系统处理查询"""
        try:
            # 1. 意图分类
            intent_result = self.intent_classifier.classify_query(query)
            is_professional = intent_result["intent_id"] == 1
            
            logger.info(f"意图分类结果: {intent_result['intent_label']} (置信度: {intent_result['confidence']:.3f})")
            
            # 2. 根据意图选择处理路径
            if not is_professional:
                # 通用知识，直接使用大模型
                logger.info("使用通用知识路径")
                response = self.llm_manager.generate_final_response(query, is_general=True)
                return {
                    "reply": response["reply"],
                    "intent": intent_result,
                    "path": "general_knowledge",
                    "documents": [],
                    "optimization": None
                }
            
            # 3. 专业性咨询，使用查询优化和文档检索
            logger.info("使用专业性咨询路径")
            
            # 查询优化
            optimization_result = self.query_optimizer.optimize_query(query)
            logger.info(f"查询优化策略: {optimization_result['strategy']}")
            
            # 文档检索
            documents = self._retrieve_documents(query, optimization_result)
            
            # 生成最终回复
            response = self.llm_manager.generate_final_response(query, documents)
            
            return {
                "reply": response["reply"],
                "intent": intent_result,
                "path": "professional_consultation",
                "documents": documents,
                "optimization": optimization_result
            }
            
        except Exception as e:
            logger.error(f"RAG处理失败: {e}")
            # 回退到通用回复
            response = self.llm_manager.generate_final_response(query, is_general=True)
            return {
                "reply": response["reply"],
                "intent": {"intent_label": "通用知识", "confidence": 0.5},
                "path": "fallback",
                "documents": [],
                "optimization": None,
                "error": str(e)
            }
    
    def _retrieve_documents(self, query: str, optimization_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检索相关文档"""
        try:
            # 获取查询的向量表示
            query_embedding = self.embedding_manager.get_query_embedding(query)
            sparse_embedding = self.embedding_manager.get_sparse_embedding(query)
            
            # 使用混合搜索
            child_documents = self.milvus_client.hybrid_search(
                query_vector=query_embedding[0],
                sparse_vector=sparse_embedding,
                top_k=self.config.TOP_K
            )
            
            if not child_documents:
                logger.warning("未检索到相关子文档")
                return []
            
            # 获取父文档
            child_ids = [doc["doc_id"] for doc in child_documents]
            parent_documents = self.milvus_client.get_parent_documents(child_ids)
            
            # 合并子文档和父文档信息
            final_documents = []
            for child_doc in child_documents:
                # 查找对应的父文档
                parent_doc = next((p for p in parent_documents if p["doc_id"] == child_doc["parent_id"]), None)
                
                if parent_doc:
                    # 合并信息
                    final_doc = {
                        "doc_id": child_doc["doc_id"],
                        "parent_id": child_doc["parent_id"],
                        "title": parent_doc.get("title", child_doc.get("title", "")),
                        "content": f"{parent_doc.get('content', '')}\n\n{child_doc.get('content', '')}",
                        "category": child_doc.get("category", ""),
                        "similarity": child_doc.get("similarity", 0.0),
                        "combined_score": child_doc.get("combined_score", 0.0)
                    }
                    final_documents.append(final_doc)
            
            # 按相似度排序并限制数量
            final_documents.sort(key=lambda x: x.get("combined_score", 0.0), reverse=True)
            final_documents = final_documents[:self.config.TOP_M]
            
            logger.info(f"检索到{len(final_documents)}个相关文档")
            return final_documents
            
        except Exception as e:
            logger.error(f"文档检索失败: {e}")
            return []
    
    def _log_query(self, user_id: str, query: str, response: str, source: str, response_time: float):
        """记录查询日志"""
        try:
            self.mysql_client.log_query(user_id or "anonymous", query, response, source, response_time)
        except Exception as e:
            logger.error(f"查询日志记录失败: {e}")
    
    def _build_response(self, 
                       query: str, 
                       reply: str, 
                       source: str, 
                       response_time: float,
                       user_id: str = None,
                       session_id: str = None,
                       rag_details: Dict[str, Any] = None,
                       error: str = None) -> Dict[str, Any]:
        """构建响应"""
        response = {
            "query": query,
            "reply": reply,
            "source": source,
            "response_time": round(response_time, 3),
            "timestamp": time.time(),
            "user_id": user_id,
            "session_id": session_id
        }
        
        if rag_details:
            response["rag_details"] = rag_details
        
        if error:
            response["error"] = error
        
        return response
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            status = {
                "mysql": self.mysql_client.get_qa_statistics(),
                "redis": self.redis_client.get_cache_stats(),
                "milvus": self.milvus_client.get_collection_stats(),
                "llm": self.llm_manager.get_usage_stats(),
                "intent_classifier": {
                    "status": "active" if self.intent_classifier else "inactive"
                },
                "embedding_model": {
                    "dimension": self.embedding_manager.get_embedding_dimension() if self.embedding_manager else 0
                }
            }
            return status
        except Exception as e:
            logger.error(f"获取系统状态失败: {e}")
            return {"error": str(e)}
    
    def add_qa_pair(self, question: str, answer: str, category: str = None) -> bool:
        """添加新的问答对"""
        try:
            # 添加到MySQL
            success = self.mysql_client.insert_qa(question, answer, category)
            if success:
                # 同时缓存到Redis
                self._cache_response(question, answer)
                logger.info(f"成功添加问答对: {question[:50]}...")
            
            return success
        except Exception as e:
            logger.error(f"添加问答对失败: {e}")
            return False
    
    def get_hot_queries(self, limit: int = 10) -> List[tuple]:
        """获取热门查询"""
        try:
            return self.redis_client.get_hot_queries(limit)
        except Exception as e:
            logger.error(f"获取热门查询失败: {e}")
            return []
    
    def close(self):
        """关闭所有连接"""
        try:
            if self.mysql_client:
                self.mysql_client.close()
            if self.redis_client:
                self.redis_client.close()
            if self.milvus_client:
                self.milvus_client.close()
            logger.info("RAG引擎已关闭")
        except Exception as e:
            logger.error(f"关闭RAG引擎失败: {e}")

# 导入配置
from config import Config


