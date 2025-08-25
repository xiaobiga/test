import re
from typing import List, Dict, Any, Tuple
from loguru import logger
import jieba
import jieba.posseg as pseg

class QueryOptimizer:
    """查询优化器 - 实现四种优化策略"""
    
    def __init__(self):
        self.config = Config()
        self._init_jieba()
    
    def _init_jieba(self):
        """初始化jieba分词"""
        try:
            # 添加体育用品相关词汇
            sports_terms = [
                "篮球", "足球", "网球", "羽毛球", "乒乓球", "跑步", "健身", "瑜伽",
                "游泳", "骑行", "滑雪", "高尔夫", "棒球", "橄榄球", "排球",
                "护膝", "护腕", "护肘", "护踝", "护腰", "护肩", "护颈",
                "运动鞋", "运动服", "运动裤", "运动内衣", "运动袜",
                "哑铃", "杠铃", "跑步机", "动感单车", "椭圆机", "划船机"
            ]
            
            for term in sports_terms:
                jieba.add_word(term)
            
            logger.info("jieba分词器初始化完成")
        except Exception as e:
            logger.error(f"jieba分词器初始化失败: {e}")
    
    def optimize_query(self, query: str, strategy: str = "auto") -> Dict[str, Any]:
        """查询优化主函数"""
        try:
            if strategy == "auto":
                # 自动选择最佳策略
                strategy = self._select_best_strategy(query)
            
            if strategy == "direct":
                return self._direct_retrieval(query)
            elif strategy == "subquery":
                return self._subquery_retrieval(query)
            elif strategy == "backtrack":
                return self._backtrack_retrieval(query)
            elif strategy == "hypothesis":
                return self._hypothesis_retrieval(query)
            else:
                raise ValueError(f"不支持的优化策略: {strategy}")
                
        except Exception as e:
            logger.error(f"查询优化失败: {e}")
            return self._fallback_optimization(query)
    
    def _select_best_strategy(self, query: str) -> str:
        """自动选择最佳优化策略"""
        try:
            # 分析查询特征
            query_length = len(query)
            word_count = len(list(jieba.cut(query)))
            has_question_words = bool(re.search(r'[什么|怎么|如何|为什么|哪个|哪些]', query))
            has_sports_terms = self._contains_sports_terms(query)
            
            # 策略选择逻辑
            if query_length < 10 and word_count <= 3:
                return "direct"  # 短查询直接检索
            elif has_question_words and has_sports_terms:
                return "subquery"  # 包含疑问词和体育术语，使用子查询
            elif query_length > 20 and word_count > 8:
                return "backtrack"  # 长查询使用回溯
            elif has_sports_terms and not has_question_words:
                return "hypothesis"  # 体育术语但不含疑问词，使用假设
            else:
                return "direct"  # 默认直接检索
                
        except Exception as e:
            logger.error(f"策略选择失败: {e}")
            return "direct"
    
    def _direct_retrieval(self, query: str) -> Dict[str, Any]:
        """直接检索策略"""
        try:
            # 简单的查询清理和标准化
            optimized_query = self._clean_query(query)
            
            return {
                "strategy": "direct",
                "original_query": query,
                "optimized_query": optimized_query,
                "sub_queries": [optimized_query],
                "confidence": 0.9,
                "explanation": "使用直接检索策略，对查询进行标准化处理"
            }
        except Exception as e:
            logger.error(f"直接检索策略失败: {e}")
            return self._fallback_optimization(query)
    
    def _subquery_retrieval(self, query: str) -> Dict[str, Any]:
        """子查询检索策略"""
        try:
            # 分解复杂查询为多个子查询
            sub_queries = self._decompose_query(query)
            
            # 为每个子查询添加相关上下文
            enhanced_sub_queries = []
            for sub_query in sub_queries:
                enhanced_query = self._enhance_sub_query(sub_query, query)
                enhanced_sub_queries.append(enhanced_query)
            
            return {
                "strategy": "subquery",
                "original_query": query,
                "optimized_query": query,  # 保持原查询
                "sub_queries": enhanced_sub_queries,
                "confidence": 0.85,
                "explanation": f"将复杂查询分解为{len(enhanced_sub_queries)}个子查询"
            }
        except Exception as e:
            logger.error(f"子查询检索策略失败: {e}")
            return self._fallback_optimization(query)
    
    def _backtrack_retrieval(self, query: str) -> Dict[str, Any]:
        """回溯问题检索策略"""
        try:
            # 识别查询中的关键概念
            key_concepts = self._extract_key_concepts(query)
            
            # 生成回溯查询
            backtrack_queries = []
            for concept in key_concepts:
                # 为每个关键概念生成更基础的查询
                base_query = self._generate_base_query(concept)
                backtrack_queries.append(base_query)
            
            # 添加原查询
            all_queries = [query] + backtrack_queries
            
            return {
                "strategy": "backtrack",
                "original_query": query,
                "optimized_query": query,
                "sub_queries": all_queries,
                "confidence": 0.8,
                "explanation": f"识别出{len(key_concepts)}个关键概念，生成回溯查询"
            }
        except Exception as e:
            logger.error(f"回溯检索策略失败: {e}")
            return self._fallback_optimization(query)
    
    def _hypothesis_retrieval(self, query: str) -> Dict[str, Any]:
        """假设答案检索策略"""
        try:
            # 基于查询生成假设答案
            hypotheses = self._generate_hypotheses(query)
            
            # 将假设答案转换为查询
            hypothesis_queries = []
            for hypothesis in hypotheses:
                hypothesis_query = self._hypothesis_to_query(hypothesis, query)
                hypothesis_queries.append(hypothesis_query)
            
            # 组合原查询和假设查询
            all_queries = [query] + hypothesis_queries
            
            return {
                "strategy": "hypothesis",
                "original_query": query,
                "optimized_query": query,
                "sub_queries": all_queries,
                "confidence": 0.75,
                "explanation": f"生成{len(hypotheses)}个假设答案，转换为相关查询"
            }
        except Exception as e:
            logger.error(f"假设检索策略失败: {e}")
            return self._fallback_optimization(query)
    
    def _clean_query(self, query: str) -> str:
        """清理和标准化查询"""
        try:
            # 去除多余空格
            cleaned = re.sub(r'\s+', ' ', query.strip())
            
            # 标准化标点符号
            cleaned = re.sub(r'[？?]', '?', cleaned)
            cleaned = re.sub(r'[！!]', '!', cleaned)
            
            # 去除特殊字符
            cleaned = re.sub(r'[^\w\s\u4e00-\u9fff?！!]', '', cleaned)
            
            return cleaned
        except Exception as e:
            logger.error(f"查询清理失败: {e}")
            return query
    
    def _decompose_query(self, query: str) -> List[str]:
        """分解复杂查询"""
        try:
            # 使用jieba进行词性标注
            words = pseg.cut(query)
            
            # 识别名词短语和动词短语
            noun_phrases = []
            verb_phrases = []
            current_noun = []
            current_verb = []
            
            for word, flag in words:
                if flag.startswith('n'):  # 名词
                    current_noun.append(word)
                    if current_verb:
                        verb_phrases.append(''.join(current_verb))
                        current_verb = []
                elif flag.startswith('v'):  # 动词
                    current_verb.append(word)
                    if current_noun:
                        noun_phrases.append(''.join(current_noun))
                        current_noun = []
                else:
                    if current_noun:
                        noun_phrases.append(''.join(current_noun))
                        current_noun = []
                    if current_verb:
                        verb_phrases.append(''.join(current_verb))
                        current_verb = []
            
            # 处理剩余的词组
            if current_noun:
                noun_phrases.append(''.join(current_noun))
            if current_verb:
                verb_phrases.append(''.join(current_verb))
            
            # 生成子查询
            sub_queries = []
            for noun in noun_phrases:
                if len(noun) > 1:  # 过滤单字词
                    sub_queries.append(noun)
            
            for verb in verb_phrases:
                if len(verb) > 1:
                    sub_queries.append(verb)
            
            return sub_queries[:5]  # 限制子查询数量
            
        except Exception as e:
            logger.error(f"查询分解失败: {e}")
            return [query]
    
    def _enhance_sub_query(self, sub_query: str, original_query: str) -> str:
        """增强子查询"""
        try:
            # 添加体育用品相关上下文
            sports_context = self._get_sports_context(original_query)
            
            if sports_context:
                enhanced = f"{sub_query} {sports_context}"
            else:
                enhanced = sub_query
            
            return enhanced
        except Exception as e:
            logger.error(f"子查询增强失败: {e}")
            return sub_query
    
    def _extract_key_concepts(self, query: str) -> List[str]:
        """提取关键概念"""
        try:
            # 使用jieba提取关键词
            words = jieba.analyse.extract_tags(query, topK=5, withWeight=False)
            
            # 过滤停用词
            stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
            key_concepts = [word for word in words if word not in stop_words and len(word) > 1]
            
            return key_concepts[:3]  # 限制概念数量
            
        except Exception as e:
            logger.error(f"关键概念提取失败: {e}")
            return []
    
    def _generate_base_query(self, concept: str) -> str:
        """生成基础查询"""
        try:
            # 为关键概念生成更基础的查询
            base_queries = [
                f"什么是{concept}",
                f"{concept}的特点",
                f"{concept}的用途",
                f"{concept}的分类"
            ]
            
            return base_queries[0]  # 返回第一个基础查询
            
        except Exception as e:
            logger.error(f"基础查询生成失败: {e}")
            return concept
    
    def _generate_hypotheses(self, query: str) -> List[str]:
        """生成假设答案"""
        try:
            # 基于查询类型生成假设
            if '?' in query or '？' in query:
                # 疑问句，生成可能的答案
                hypotheses = [
                    f"关于{query.replace('?', '').replace('？', '')}的解答",
                    f"{query.replace('?', '').replace('？', '')}的相关信息",
                    f"{query.replace('?', '').replace('？', '')}的详细说明"
                ]
            else:
                # 陈述句，生成相关查询
                hypotheses = [
                    f"{query}的特点",
                    f"{query}的用途",
                    f"{query}的推荐",
                    f"{query}的对比"
                ]
            
            return hypotheses[:3]  # 限制假设数量
            
        except Exception as e:
            logger.error(f"假设生成失败: {e}")
            return []
    
    def _hypothesis_to_query(self, hypothesis: str, original_query: str) -> str:
        """将假设转换为查询"""
        try:
            # 将假设转换为更具体的查询
            if '特点' in hypothesis:
                return f"{original_query} 特点 优势"
            elif '用途' in hypothesis:
                return f"{original_query} 用途 应用场景"
            elif '推荐' in hypothesis:
                return f"{original_query} 推荐 选择"
            elif '对比' in hypothesis:
                return f"{original_query} 对比 区别"
            else:
                return hypothesis
                
        except Exception as e:
            logger.error(f"假设转换失败: {e}")
            return hypothesis
    
    def _contains_sports_terms(self, query: str) -> bool:
        """检查是否包含体育术语"""
        try:
            sports_terms = [
                "篮球", "足球", "网球", "羽毛球", "乒乓球", "跑步", "健身", "瑜伽",
                "游泳", "骑行", "滑雪", "高尔夫", "棒球", "橄榄球", "排球"
            ]
            
            return any(term in query for term in sports_terms)
            
        except Exception as e:
            logger.error(f"体育术语检查失败: {e}")
            return False
    
    def _get_sports_context(self, query: str) -> str:
        """获取体育用品上下文"""
        try:
            # 根据查询内容返回相关上下文
            if any(term in query for term in ["篮球", "足球", "网球"]):
                return "运动装备"
            elif any(term in query for term in ["跑步", "健身", "瑜伽"]):
                return "健身器材"
            elif any(term in query for term in ["护膝", "护腕", "护肘"]):
                return "防护装备"
            else:
                return "体育用品"
                
        except Exception as e:
            logger.error(f"体育上下文获取失败: {e}")
            return ""
    
    def _fallback_optimization(self, query: str) -> Dict[str, Any]:
        """回退优化策略"""
        return {
            "strategy": "fallback",
            "original_query": query,
            "optimized_query": query,
            "sub_queries": [query],
            "confidence": 0.5,
            "explanation": "使用回退策略，保持原查询不变"
        }

# 导入配置
from config import Config


