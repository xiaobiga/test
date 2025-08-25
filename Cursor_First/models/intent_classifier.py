import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import BertTokenizer, BertModel, AutoTokenizer, AutoModel
from typing import Dict, List, Tuple
import numpy as np
from loguru import logger
from config import Config

class IntentClassifier(nn.Module):
    """意图分类器 - 基于BERT的二分类模型"""
    
    def __init__(self, model_name: str = None, num_classes: int = 2):
        super(IntentClassifier, self).__init__()
        self.config = Config()
        self.model_name = model_name or self.config.BERT_MODEL_NAME
        self.num_classes = num_classes
        
        # 加载预训练模型
        try:
            self.bert = AutoModel.from_pretrained(self.model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            logger.info(f"加载预训练模型成功: {self.model_name}")
        except Exception as e:
            logger.error(f"加载预训练模型失败: {e}")
            # 回退到默认模型
            self.bert = AutoModel.from_pretrained("bert-base-chinese")
            self.tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
        
        # 分类头
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)
        
        # 意图标签映射
        self.intent_labels = {
            0: "通用知识",
            1: "专业性咨询"
        }
        
        # 移动到GPU（如果可用）
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.to(self.device)
        
        logger.info(f"意图分类器初始化完成，使用设备: {self.device}")
    
    def forward(self, input_ids, attention_mask=None, token_type_ids=None):
        """前向传播"""
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids
        )
        
        # 使用[CLS]标记的输出进行分类
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        
        return logits
    
    def predict_intent(self, text: str) -> Tuple[int, str, float]:
        """预测文本的意图"""
        try:
            # 预处理文本
            inputs = self.tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            )
            
            # 移动到设备
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 推理
            self.eval()
            with torch.no_grad():
                logits = self(**inputs)
                probabilities = F.softmax(logits, dim=1)
                predicted_class = torch.argmax(probabilities, dim=1).item()
                confidence = probabilities[0][predicted_class].item()
            
            intent_label = self.intent_labels[predicted_class]
            
            logger.info(f"意图分类结果: {text[:50]}... -> {intent_label} (置信度: {confidence:.3f})")
            
            return predicted_class, intent_label, confidence
            
        except Exception as e:
            logger.error(f"意图分类失败: {e}")
            # 返回默认结果
            return 0, "通用知识", 0.5
    
    def batch_predict(self, texts: List[str]) -> List[Tuple[int, str, float]]:
        """批量预测意图"""
        results = []
        for text in texts:
            result = self.predict_intent(text)
            results.append(result)
        return results
    
    def get_intent_features(self, text: str) -> np.ndarray:
        """获取文本的意图特征向量"""
        try:
            inputs = self.tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            self.eval()
            with torch.no_grad():
                outputs = self.bert(**inputs)
                # 使用平均池化获取特征
                features = torch.mean(outputs.last_hidden_state, dim=1)
                return features.cpu().numpy()
                
        except Exception as e:
            logger.error(f"获取意图特征失败: {e}")
            return np.zeros((1, 768))
    
    def save_model(self, save_path: str):
        """保存模型"""
        try:
            torch.save({
                'model_state_dict': self.state_dict(),
                'config': self.bert.config,
                'intent_labels': self.intent_labels
            }, save_path)
            logger.info(f"模型保存成功: {save_path}")
        except Exception as e:
            logger.error(f"模型保存失败: {e}")
    
    def load_model(self, load_path: str):
        """加载模型"""
        try:
            checkpoint = torch.load(load_path, map_location=self.device)
            self.load_state_dict(checkpoint['model_state_dict'])
            self.intent_labels = checkpoint.get('intent_labels', self.intent_labels)
            logger.info(f"模型加载成功: {load_path}")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")

class IntentClassifierManager:
    """意图分类器管理器"""
    
    def __init__(self):
        self.classifier = None
        self._load_classifier()
    
    def _load_classifier(self):
        """加载意图分类器"""
        try:
            self.classifier = IntentClassifier()
            logger.info("意图分类器管理器初始化完成")
        except Exception as e:
            logger.error(f"意图分类器管理器初始化失败: {e}")
            raise
    
    def classify_query(self, query: str) -> Dict[str, any]:
        """分类用户查询"""
        try:
            if not self.classifier:
                raise Exception("意图分类器未初始化")
            
            intent_id, intent_label, confidence = self.classifier.predict_intent(query)
            
            return {
                "intent_id": intent_id,
                "intent_label": intent_label,
                "confidence": confidence,
                "query": query
            }
            
        except Exception as e:
            logger.error(f"查询分类失败: {e}")
            return {
                "intent_id": 0,
                "intent_label": "通用知识",
                "confidence": 0.5,
                "query": query,
                "error": str(e)
            }
    
    def is_professional_query(self, query: str, threshold: float = 0.7) -> bool:
        """判断是否为专业性咨询"""
        try:
            result = self.classify_query(query)
            return result["intent_id"] == 1 and result["confidence"] >= threshold
        except Exception as e:
            logger.error(f"专业性判断失败: {e}")
            return False


