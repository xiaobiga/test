from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn
from loguru import logger
import time
import uuid

from core.rag_engine import RAGEngine

# 创建FastAPI应用
app = FastAPI(
    title="体育用品电商AI客服RAG系统",
    description="基于RAG的智能客服系统，提供专业的体育用品咨询和问答服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局RAG引擎实例
rag_engine = None

# 请求模型
class QueryRequest(BaseModel):
    query: str = Field(..., description="用户查询", min_length=1, max_length=1000)
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")

class QAPairRequest(BaseModel):
    question: str = Field(..., description="问题", min_length=1, max_length=1000)
    answer: str = Field(..., description="答案", min_length=1, max_length=5000)
    category: Optional[str] = Field(None, description="分类")

class DocumentRequest(BaseModel):
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="文档内容")
    category: Optional[str] = Field(None, description="文档分类")
    parent_id: Optional[str] = Field(None, description="父文档ID")

# 响应模型
class QueryResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str
    timestamp: float

class StatusResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str

# 依赖函数
def get_rag_engine():
    """获取RAG引擎实例"""
    global rag_engine
    if rag_engine is None:
        try:
            rag_engine = RAGEngine()
        except Exception as e:
            logger.error(f"RAG引擎初始化失败: {e}")
            raise HTTPException(status_code=500, detail="系统初始化失败")
    return rag_engine

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("体育用品电商AI客服RAG系统启动中...")
    try:
        # 初始化RAG引擎
        global rag_engine
        rag_engine = RAGEngine()
        logger.info("RAG引擎初始化成功")
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        raise

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("系统关闭中...")
    if rag_engine:
        rag_engine.close()
    logger.info("系统已关闭")

# 健康检查
@app.get("/health", response_model=StatusResponse)
async def health_check():
    """健康检查接口"""
    try:
        return StatusResponse(
            success=True,
            data={"status": "healthy", "timestamp": time.time()},
            message="系统运行正常"
        )
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return StatusResponse(
            success=False,
            data={"status": "unhealthy", "error": str(e)},
            message="系统异常"
        )

# 主要查询接口
@app.post("/api/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    rag_engine: RAGEngine = Depends(get_rag_engine)
):
    """处理用户查询"""
    try:
        start_time = time.time()
        
        # 生成会话ID（如果没有提供）
        session_id = request.session_id or str(uuid.uuid4())
        
        # 处理查询
        response = rag_engine.process_query(
            query=request.query,
            user_id=request.user_id,
            session_id=session_id
        )
        
        # 计算总响应时间
        total_time = time.time() - start_time
        
        # 构建响应数据
        response_data = {
            "query": response["query"],
            "reply": response["reply"],
            "source": response["source"],
            "response_time": response["response_time"],
            "total_time": round(total_time, 3),
            "session_id": session_id,
            "user_id": request.user_id
        }
        
        # 添加RAG详细信息（如果有）
        if "rag_details" in response:
            response_data["rag_details"] = response["rag_details"]
        
        return QueryResponse(
            success=True,
            data=response_data,
            message="查询处理成功",
            timestamp=time.time()
        )
        
    except Exception as e:
        logger.error(f"查询处理失败: {e}")
        return QueryResponse(
            success=False,
            data={"error": str(e)},
            message="查询处理失败",
            timestamp=time.time()
        )

# 添加问答对接口
@app.post("/api/qa", response_model=StatusResponse)
async def add_qa_pair(
    request: QAPairRequest,
    rag_engine: RAGEngine = Depends(get_rag_engine)
):
    """添加新的问答对"""
    try:
        success = rag_engine.add_qa_pair(
            question=request.question,
            answer=request.answer,
            category=request.category
        )
        
        if success:
            return StatusResponse(
                success=True,
                data={"message": "问答对添加成功"},
                message="问答对添加成功"
            )
        else:
            raise HTTPException(status_code=500, detail="问答对添加失败")
            
    except Exception as e:
        logger.error(f"添加问答对失败: {e}")
        return StatusResponse(
            success=False,
            data={"error": str(e)},
            message="添加问答对失败"
        )

# 获取系统状态接口
@app.get("/api/status", response_model=StatusResponse)
async def get_system_status(
    rag_engine: RAGEngine = Depends(get_rag_engine)
):
    """获取系统状态"""
    try:
        status = rag_engine.get_system_status()
        return StatusResponse(
            success=True,
            data=status,
            message="系统状态获取成功"
        )
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return StatusResponse(
            success=False,
            data={"error": str(e)},
            message="获取系统状态失败"
        )

# 获取热门查询接口
@app.get("/api/hot-queries", response_model=StatusResponse)
async def get_hot_queries(
    limit: int = 10,
    rag_engine: RAGEngine = Depends(get_rag_engine)
):
    """获取热门查询"""
    try:
        hot_queries = rag_engine.get_hot_queries(limit)
        return StatusResponse(
            success=True,
            data={"hot_queries": hot_queries},
            message="热门查询获取成功"
        )
    except Exception as e:
        logger.error(f"获取热门查询失败: {e}")
        return StatusResponse(
            success=False,
            data={"error": str(e)},
            message="获取热门查询失败"
        )

# 批量查询接口
@app.post("/api/batch-query", response_model=StatusResponse)
async def batch_process_queries(
    requests: List[QueryRequest],
    rag_engine: RAGEngine = Depends(get_rag_engine)
):
    """批量处理查询"""
    try:
        if len(requests) > 10:  # 限制批量查询数量
            raise HTTPException(status_code=400, detail="批量查询数量不能超过10个")
        
        results = []
        for request in requests:
            try:
                response = rag_engine.process_query(
                    query=request.query,
                    user_id=request.user_id,
                    session_id=request.session_id
                )
                results.append(response)
            except Exception as e:
                results.append({
                    "query": request.query,
                    "reply": f"处理失败: {str(e)}",
                    "error": str(e)
                })
        
        return StatusResponse(
            success=True,
            data={"results": results},
            message=f"批量查询完成，共处理{len(requests)}个查询"
        )
        
    except Exception as e:
        logger.error(f"批量查询失败: {e}")
        return StatusResponse(
            success=False,
            data={"error": str(e)},
            message="批量查询失败"
        )

# 测试接口
@app.get("/api/test", response_model=StatusResponse)
async def test_system():
    """测试系统功能"""
    try:
        # 这里可以添加各种系统测试
        test_results = {
            "api": "正常",
            "timestamp": time.time()
        }
        
        return StatusResponse(
            success=True,
            data=test_results,
            message="系统测试通过"
        )
        
    except Exception as e:
        logger.error(f"系统测试失败: {e}")
        return StatusResponse(
            success=False,
            data={"error": str(e)},
            message="系统测试失败"
        )

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "体育用品电商AI客服RAG系统",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"全局异常: {exc}")
    return {
        "success": False,
        "message": "系统内部错误",
        "error": str(exc)
    }

if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


