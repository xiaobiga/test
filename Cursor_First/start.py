#!/usr/bin/env python3
"""
体育用品电商AI客服RAG系统启动脚本
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    print("检查系统依赖...")
    
    try:
        import fastapi
        import uvicorn
        import pymysql
        import redis
        import pymilvus
        import torch
        import transformers
        import sentence_transformers
        import openai
        print("✓ 所有Python依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_environment():
    """检查环境配置"""
    print("检查环境配置...")
    
    # 检查.env文件
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠ 未找到.env文件，请复制env_example.txt为.env并配置")
        return False
    
    # 检查必要的环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD",
        "REDIS_HOST", "MILVUS_HOST", "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ 缺少环境变量: {', '.join(missing_vars)}")
        return False
    
    print("✓ 环境配置检查通过")
    return True

def check_services():
    """检查外部服务状态"""
    print("检查外部服务状态...")
    
    # 这里可以添加服务检查逻辑
    # 例如检查MySQL、Redis、Milvus是否运行
    
    print("⚠ 请确保以下服务正在运行:")
    print("  - MySQL数据库")
    print("  - Redis缓存服务")
    print("  - Milvus向量数据库")
    
    return True

def init_database():
    """初始化数据库"""
    print("初始化数据库...")
    
    try:
        from scripts.init_database import init_database as init_db
        init_db()
        print("✓ 数据库初始化成功")
        return True
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        return False

def start_system():
    """启动系统"""
    print("启动RAG系统...")
    
    try:
        # 启动FastAPI服务
        api_path = Path("api/main.py")
        if api_path.exists():
            print("启动API服务...")
            subprocess.run([sys.executable, str(api_path)], check=True)
        else:
            print("✗ 未找到API主文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ 系统启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n系统被用户中断")
        return True

def main():
    """主函数"""
    print("=" * 60)
    print("体育用品电商AI客服RAG系统")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查环境
    if not check_environment():
        return
    
    # 检查服务
    if not check_services():
        return
    
    # 询问是否初始化数据库
    print("\n是否要初始化数据库？(y/n): ", end="")
    choice = input().lower().strip()
    
    if choice in ['y', 'yes', '是']:
        if not init_database():
            print("数据库初始化失败，请检查配置后重试")
            return
    
    # 启动系统
    print("\n准备启动系统...")
    time.sleep(2)
    
    if start_system():
        print("系统启动完成")
    else:
        print("系统启动失败")

if __name__ == "__main__":
    main()


