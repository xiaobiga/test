import os
import json
import uuid
from typing import List, Dict, Any, Tuple
from loguru import logger
import re

class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self):
        self.config = Config()
    
    def process_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理文档列表"""
        try:
            processed_docs = []
            
            for doc in documents:
                processed_doc = self._process_single_document(doc)
                if processed_doc:
                    processed_docs.append(processed_doc)
            
            logger.info(f"成功处理{len(processed_docs)}个文档")
            return processed_docs
            
        except Exception as e:
            logger.error(f"文档处理失败: {e}")
            return []
    
    def _process_single_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个文档"""
        try:
            # 提取基本信息
            title = document.get("title", "")
            content = document.get("content", "")
            category = document.get("category", "未分类")
            
            if not content:
                logger.warning(f"文档内容为空: {title}")
                return None
            
            # 清理和标准化内容
            cleaned_content = self._clean_content(content)
            if not cleaned_content:
                return None
            
            # 生成文档ID
            doc_id = document.get("doc_id") or str(uuid.uuid4())
            
            # 分割文档为父子块
            parent_blocks, child_blocks = self._split_document(
                title, cleaned_content, category, doc_id
            )
            
            # 合并结果
            all_blocks = parent_blocks + child_blocks
            
            return {
                "original_doc": document,
                "processed_blocks": all_blocks,
                "parent_count": len(parent_blocks),
                "child_count": len(child_blocks)
            }
            
        except Exception as e:
            logger.error(f"单个文档处理失败: {e}")
            return None
    
    def _clean_content(self, content: str) -> str:
        """清理文档内容"""
        try:
            if not content:
                return ""
            
            # 去除多余空白字符
            content = re.sub(r'\s+', ' ', content.strip())
            
            # 去除特殊字符（保留中文、英文、数字、基本标点）
            content = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()（）【】""''、，。！？；：\n]', '', content)
            
            # 标准化换行符
            content = re.sub(r'\n+', '\n', content)
            
            return content
            
        except Exception as e:
            logger.error(f"内容清理失败: {e}")
            return content
    
    def _split_document(self, 
                        title: str, 
                        content: str, 
                        category: str, 
                        doc_id: str) -> Tuple[List[Dict], List[Dict]]:
        """分割文档为父子块"""
        try:
            # 按段落分割
            paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
            
            if not paragraphs:
                return [], []
            
            parent_blocks = []
            child_blocks = []
            
            # 创建父块（包含标题和主要段落）
            parent_content = f"{title}\n\n{paragraphs[0]}"
            if len(paragraphs) > 1:
                parent_content += f"\n\n{paragraphs[1]}"
            
            parent_block = {
                "doc_id": f"{doc_id}_parent",
                "parent_id": None,
                "child_id": f"{doc_id}_child",
                "title": title,
                "content": parent_content,
                "category": category,
                "block_type": "parent",
                "length": len(parent_content)
            }
            parent_blocks.append(parent_block)
            
            # 创建子块（详细内容）
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph) < 10:  # 跳过过短的段落
                    continue
                
                child_block = {
                    "doc_id": f"{doc_id}_child_{i}",
                    "parent_id": f"{doc_id}_parent",
                    "child_id": None,
                    "title": f"{title} - 段落{i+1}",
                    "content": paragraph,
                    "category": category,
                    "block_type": "child",
                    "length": len(paragraph),
                    "paragraph_index": i
                }
                child_blocks.append(child_block)
            
            return parent_blocks, child_blocks
            
        except Exception as e:
            logger.error(f"文档分割失败: {e}")
            return [], []
    
    def process_sports_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理体育用品相关文档"""
        try:
            processed_docs = []
            
            for doc in documents:
                # 添加体育用品相关的元数据
                enhanced_doc = self._enhance_sports_document(doc)
                processed_doc = self._process_single_document(enhanced_doc)
                
                if processed_doc:
                    processed_docs.append(processed_doc)
            
            return processed_docs
            
        except Exception as e:
            logger.error(f"体育用品文档处理失败: {e}")
            return []
    
    def _enhance_sports_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """增强体育用品文档"""
        try:
            enhanced_doc = document.copy()
            
            # 添加体育用品相关标签
            sports_keywords = self._extract_sports_keywords(document.get("content", ""))
            if sports_keywords:
                enhanced_doc["sports_keywords"] = sports_keywords
            
            # 添加产品类型分类
            product_type = self._classify_product_type(document.get("content", ""))
            if product_type:
                enhanced_doc["product_type"] = product_type
            
            # 添加适用运动分类
            sport_category = self._classify_sport_category(document.get("content", ""))
            if sport_category:
                enhanced_doc["sport_category"] = sport_category
            
            return enhanced_doc
            
        except Exception as e:
            logger.error(f"文档增强失败: {e}")
            return document
    
    def _extract_sports_keywords(self, content: str) -> List[str]:
        """提取体育用品关键词"""
        try:
            # 体育用品相关词汇
            sports_terms = [
                "篮球", "足球", "网球", "羽毛球", "乒乓球", "跑步", "健身", "瑜伽",
                "游泳", "骑行", "滑雪", "高尔夫", "棒球", "橄榄球", "排球",
                "护膝", "护腕", "护肘", "护踝", "护腰", "护肩", "护颈",
                "运动鞋", "运动服", "运动裤", "运动内衣", "运动袜",
                "哑铃", "杠铃", "跑步机", "动感单车", "椭圆机", "划船机"
            ]
            
            found_keywords = []
            for term in sports_terms:
                if term in content:
                    found_keywords.append(term)
            
            return found_keywords[:5]  # 限制关键词数量
            
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return []
    
    def _classify_product_type(self, content: str) -> str:
        """分类产品类型"""
        try:
            if any(term in content for term in ["护膝", "护腕", "护肘", "护踝", "护腰", "护肩", "护颈"]):
                return "防护装备"
            elif any(term in content for term in ["运动鞋", "运动服", "运动裤", "运动内衣", "运动袜"]):
                return "运动服装"
            elif any(term in content for term in ["哑铃", "杠铃", "跑步机", "动感单车", "椭圆机", "划船机"]):
                return "健身器材"
            elif any(term in content for term in ["篮球", "足球", "网球", "羽毛球", "乒乓球"]):
                return "运动器材"
            else:
                return "其他"
                
        except Exception as e:
            logger.error(f"产品类型分类失败: {e}")
            return "其他"
    
    def _classify_sport_category(self, content: str) -> str:
        """分类适用运动"""
        try:
            if any(term in content for term in ["篮球", "足球", "网球", "羽毛球", "乒乓球"]):
                return "球类运动"
            elif any(term in content for term in ["跑步", "健身", "瑜伽"]):
                return "健身运动"
            elif any(term in content for term in ["游泳", "骑行", "滑雪"]):
                return "户外运动"
            elif any(term in content for term in ["高尔夫", "棒球", "橄榄球", "排球"]):
                return "专业运动"
            else:
                return "通用"
                
        except Exception as e:
            logger.error(f"运动分类失败: {e}")
            return "通用"

class VectorGenerator:
    """向量生成器"""
    
    def __init__(self, embedding_manager):
        self.embedding_manager = embedding_manager
    
    def generate_document_vectors(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """为文档生成向量"""
        try:
            vectorized_docs = []
            
            for doc in documents:
                vectorized_doc = self._generate_single_document_vectors(doc)
                if vectorized_doc:
                    vectorized_docs.append(vectorized_doc)
            
            logger.info(f"成功生成{len(vectorized_docs)}个文档的向量")
            return vectorized_docs
            
        except Exception as e:
            logger.error(f"向量生成失败: {e}")
            return []
    
    def _generate_single_document_vectors(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """为单个文档生成向量"""
        try:
            processed_blocks = document.get("processed_blocks", [])
            if not processed_blocks:
                return None
            
            vectorized_blocks = []
            
            for block in processed_blocks:
                vectorized_block = self._vectorize_block(block)
                if vectorized_block:
                    vectorized_blocks.append(vectorized_block)
            
            return {
                "original_doc": document.get("original_doc", {}),
                "vectorized_blocks": vectorized_blocks
            }
            
        except Exception as e:
            logger.error(f"单个文档向量化失败: {e}")
            return None
    
    def _vectorize_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """向量化文档块"""
        try:
            content = block.get("content", "")
            if not content:
                return None
            
            # 生成稠密向量
            dense_vector = self.embedding_manager.get_document_embedding(content)
            
            # 生成稀疏向量
            sparse_vector = self.embedding_manager.get_sparse_embedding(content)
            
            vectorized_block = block.copy()
            vectorized_block["dense_vector"] = dense_vector[0].tolist() if dense_vector.size > 0 else []
            vectorized_block["sparse_vector"] = sparse_vector.tolist() if sparse_vector.size > 0 else []
            
            return vectorized_block
            
        except Exception as e:
            logger.error(f"文档块向量化失败: {e}")
            return None

# 导入配置
from config import Config


