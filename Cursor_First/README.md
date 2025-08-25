# 体育用品电商AI客服RAG系统

## 项目简介

这是一个基于RAG（Retrieval-Augmented Generation）的智能客服系统，专门为体育用品电商平台设计。系统通过结合MySQL数据库、Redis缓存、Milvus向量数据库和大语言模型，为用户提供高效、准确、专业的体育用品咨询服务。

## 系统架构

```
用户查询 → MySQL数据库 → Redis缓存 → RAG系统 → 大模型回复
                ↓
        意图分类模块 → 查询优化模块 → 文档检索模块
                ↓
        通用知识路径    专业性咨询路径
                ↓
        直接回复        策略优化 + 向量检索 + 上下文生成
```

## 核心特性

### 1. 多层检索策略
- **MySQL优先**：高频问答直接返回，响应最快
- **Redis缓存**：热门问题缓存，提升响应速度
- **RAG系统**：复杂问题深度处理，提供专业答案

### 2. 智能意图分类
- 基于BERT的二分类模型
- 区分通用知识和专业性咨询
- 自动选择最优处理路径

### 3. 查询优化策略
- **直接检索**：简单查询标准化处理
- **子查询检索**：复杂查询分解优化
- **回溯问题检索**：关键概念深度挖掘
- **假设答案检索**：基于假设的扩展查询

### 4. 混合向量检索
- BGE-M3模型生成稠密向量
- TF-IDF生成稀疏向量
- 权重聚合的混合搜索
- 父子文档结构优化

### 5. 专业体育知识
- 体育用品分类体系
- 运动项目专业术语
- 产品特性智能识别
- 用户需求精准匹配

## 技术栈

### 后端框架
- **FastAPI**: 高性能异步Web框架
- **Uvicorn**: ASGI服务器

### 数据库
- **MySQL**: 结构化数据存储
- **Redis**: 缓存和会话管理
- **Milvus**: 向量数据库

### AI模型
- **BERT**: 意图分类
- **BGE-M3**: 文本向量化
- **OpenAI GPT**: 大语言模型

### 工具库
- **PyTorch**: 深度学习框架
- **Transformers**: 预训练模型
- **Sentence-Transformers**: 句子向量化
- **jieba**: 中文分词

## 安装部署

### 环境要求
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+
- Milvus 2.3+

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd sports-rag-system
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，配置数据库连接信息
```

4. **初始化数据库**
```bash
# 启动MySQL、Redis、Milvus服务
# 系统会自动创建必要的表结构
```

5. **启动服务**
```bash
python api/main.py
```

### 环境变量配置

```env
# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=sports_qa

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Milvus配置
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION=sports_docs

# OpenAI配置
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-3.5-turbo

# 模型配置
BERT_MODEL_NAME=bert-base-chinese
BGE_MODEL_NAME=BAAI/bge-m3
```

## API接口

### 主要接口

#### 1. 查询接口
```http
POST /api/query
Content-Type: application/json

{
    "query": "篮球鞋怎么选择？",
    "user_id": "user123",
    "session_id": "session456"
}
```

#### 2. 添加问答对
```http
POST /api/qa
Content-Type: application/json

{
    "question": "跑步机有哪些品牌？",
    "answer": "主流品牌包括...",
    "category": "健身器材"
}
```

#### 3. 系统状态
```http
GET /api/status
```

#### 4. 热门查询
```http
GET /api/hot-queries?limit=10
```

### 接口文档
启动服务后访问：`http://localhost:8000/docs`

## 使用示例

### Python客户端

```python
import requests

# 查询示例
response = requests.post("http://localhost:8000/api/query", json={
    "query": "护膝怎么选择？",
    "user_id": "test_user"
})

print(response.json())
```

### cURL示例

```bash
curl -X POST "http://localhost:8000/api/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "篮球鞋怎么选择？", "user_id": "test_user"}'
```

## 系统监控

### 健康检查
```bash
curl http://localhost:8000/health
```

### 性能指标
- 响应时间统计
- 缓存命中率
- 向量检索准确率
- 用户满意度评分

## 扩展功能

### 1. 多语言支持
- 支持英文、日文等语言
- 多语言模型切换
- 国际化界面

### 2. 知识图谱
- 体育用品知识图谱构建
- 实体关系挖掘
- 推理能力增强

### 3. 个性化推荐
- 用户画像构建
- 个性化问答
- 推荐算法优化

### 4. 语音交互
- 语音识别集成
- 语音合成输出
- 多模态交互

## 性能优化

### 1. 缓存策略
- 多级缓存架构
- 智能缓存更新
- 缓存预热机制

### 2. 向量索引优化
- IVF索引调优
- 量化压缩
- 分布式部署

### 3. 模型优化
- 模型量化
- 推理加速
- 批量处理

## 故障排除

### 常见问题

1. **模型加载失败**
   - 检查网络连接
   - 验证模型路径
   - 确认GPU驱动

2. **数据库连接错误**
   - 检查服务状态
   - 验证连接参数
   - 确认权限设置

3. **向量检索异常**
   - 检查Milvus服务
   - 验证索引状态
   - 确认向量维度

### 日志查看
```bash
tail -f logs/sports_rag.log
```

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

- 项目维护者：[Your Name]
- 邮箱：[your.email@example.com]
- 项目地址：[GitHub Repository URL]

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础RAG功能实现
- 体育用品知识库集成
- API接口完善

---

**注意**: 本项目仅供学习和研究使用，在生产环境中使用前请进行充分的测试和验证。


