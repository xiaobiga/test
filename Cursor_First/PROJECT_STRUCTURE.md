# 项目结构说明

```
sports-rag-system/
├── README.md                    # 项目说明文档
├── PROJECT_STRUCTURE.md         # 项目结构说明（本文件）
├── requirements.txt             # Python依赖包列表
├── env_example.txt              # 环境变量配置示例
├── start.py                     # 系统启动脚本
│
├── config.py                    # 系统配置文件
│
├── database/                    # 数据库相关模块
│   ├── __init__.py
│   ├── mysql_client.py         # MySQL数据库客户端
│   └── redis_client.py         # Redis缓存客户端
│
├── models/                      # AI模型相关模块
│   ├── __init__.py
│   ├── intent_classifier.py    # 意图分类器（BERT）
│   ├── query_optimizer.py      # 查询优化策略
│   └── embedding_model.py      # 词嵌入模型（BGE-M3）
│
├── vector_store/                # 向量数据库模块
│   ├── __init__.py
│   └── milvus_client.py        # Milvus向量数据库客户端
│
├── llm/                        # 大语言模型模块
│   ├── __init__.py
│   └── openai_client.py        # OpenAI API客户端
│
├── core/                       # 核心RAG引擎
│   ├── __init__.py
│   └── rag_engine.py           # RAG引擎核心模块
│
├── api/                        # API接口层
│   ├── __init__.py
│   └── main.py                 # FastAPI主应用
│
├── utils/                      # 工具模块
│   ├── __init__.py
│   └── data_processor.py       # 数据处理工具
│
├── scripts/                    # 脚本文件
│   ├── __init__.py
│   ├── init_database.py        # 数据库初始化脚本
│   └── test_system.py          # 系统测试脚本
│
└── logs/                       # 日志目录
    └── .gitkeep               # Git占位文件
```

## 模块功能说明

### 1. 配置模块 (config.py)
- 集中管理系统配置参数
- 支持环境变量配置
- 包含数据库、模型、API等配置

### 2. 数据库模块 (database/)
- **MySQL客户端**: 存储结构化问答数据
- **Redis客户端**: 缓存高频问答对和会话信息

### 3. AI模型模块 (models/)
- **意图分类器**: 基于BERT的二分类模型，区分通用知识和专业性咨询
- **查询优化器**: 实现四种查询优化策略
- **词嵌入模型**: 基于BGE-M3的文本向量化

### 4. 向量数据库模块 (vector_store/)
- **Milvus客户端**: 存储和检索文档向量
- 支持稠密向量和稀疏向量的混合搜索

### 5. 大语言模型模块 (llm/)
- **OpenAI客户端**: 集成GPT模型生成最终回复
- 支持通用回复和RAG回复两种模式

### 6. 核心引擎 (core/)
- **RAG引擎**: 整合所有组件，实现完整的RAG流程
- 智能路由和错误处理

### 7. API接口层 (api/)
- **FastAPI应用**: 提供RESTful API接口
- 支持查询、管理、监控等功能

### 8. 工具模块 (utils/)
- **数据处理工具**: 文档处理和向量生成
- 支持体育用品专业分类

### 9. 脚本文件 (scripts/)
- **数据库初始化**: 创建表结构和初始数据
- **系统测试**: 全面的功能测试和性能测试

## 数据流向

```
用户查询 → API接口 → RAG引擎 → 数据库/缓存 → AI模型 → 向量检索 → 大模型 → 回复生成
    ↓
日志记录 ← 性能监控 ← 错误处理 ← 结果返回 ← 响应构建
```

## 扩展点

### 1. 新增模型支持
- 在 `models/` 目录下添加新的模型实现
- 在 `config.py` 中添加相应配置
- 在 `rag_engine.py` 中集成新模型

### 2. 新增数据库支持
- 在 `database/` 目录下添加新的数据库客户端
- 实现统一的接口规范
- 在配置中添加连接参数

### 3. 新增API接口
- 在 `api/main.py` 中添加新的路由
- 定义请求和响应模型
- 实现相应的业务逻辑

### 4. 新增查询策略
- 在 `models/query_optimizer.py` 中添加新策略
- 在策略选择逻辑中集成新策略
- 测试新策略的效果

## 部署说明

### 开发环境
1. 克隆项目到本地
2. 安装依赖: `pip install -r requirements.txt`
3. 配置环境变量: 复制 `env_example.txt` 为 `.env`
4. 启动服务: `python start.py`

### 生产环境
1. 使用Docker容器化部署
2. 配置负载均衡和高可用
3. 设置监控和告警
4. 定期备份数据

## 注意事项

1. **环境依赖**: 确保MySQL、Redis、Milvus服务正常运行
2. **API密钥**: 配置有效的OpenAI API密钥
3. **模型下载**: 首次运行会自动下载预训练模型
4. **资源要求**: 建议至少8GB内存，支持GPU加速
5. **网络访问**: 需要访问Hugging Face和OpenAI的API


