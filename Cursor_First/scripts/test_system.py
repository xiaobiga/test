#!/usr/bin/env python3
"""
系统测试脚本
用于测试RAG系统的各个组件功能
"""

import os
import sys
import time
import requests
from loguru import logger

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_endpoints():
    """测试API端点"""
    base_url = "http://localhost:8000"
    
    logger.info("开始测试API端点...")
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            logger.info("✓ 健康检查接口正常")
        else:
            logger.error(f"✗ 健康检查接口异常: {response.status_code}")
    except Exception as e:
        logger.error(f"✗ 健康检查接口连接失败: {e}")
    
    # 测试根路径
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            logger.info("✓ 根路径接口正常")
        else:
            logger.error(f"✗ 根路径接口异常: {response.status_code}")
    except Exception as e:
        logger.error(f"✗ 根路径接口连接失败: {e}")
    
    # 测试系统状态
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            logger.info("✓ 系统状态接口正常")
        else:
            logger.error(f"✗ 系统状态接口异常: {response.status_code}")
    except Exception as e:
        logger.error(f"✗ 系统状态接口连接失败: {e}")

def test_query_functionality():
    """测试查询功能"""
    base_url = "http://localhost:8000"
    
    logger.info("开始测试查询功能...")
    
    # 测试简单查询
    test_queries = [
        "篮球鞋怎么选择？",
        "护膝怎么戴？",
        "跑步机怎么使用？",
        "瑜伽垫怎么选择？",
        "哑铃重量怎么选择？"
    ]
    
    for query in test_queries:
        try:
            response = requests.post(f"{base_url}/api/query", json={
                "query": query,
                "user_id": "test_user",
                "session_id": f"test_session_{int(time.time())}"
            })
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"✓ 查询成功: {query[:20]}...")
                    logger.info(f"  回复来源: {result['data']['source']}")
                    logger.info(f"  响应时间: {result['data']['response_time']}s")
                else:
                    logger.error(f"✗ 查询失败: {query[:20]}... - {result.get('message')}")
            else:
                logger.error(f"✗ 查询接口异常: {response.status_code}")
                
        except Exception as e:
            logger.error(f"✗ 查询测试失败: {query[:20]}... - {e}")
        
        # 添加延迟避免请求过快
        time.sleep(1)

def test_qa_management():
    """测试问答管理功能"""
    base_url = "http://localhost:8000"
    
    logger.info("开始测试问答管理功能...")
    
    # 测试添加问答对
    test_qa = {
        "question": "测试问题：运动鞋怎么清洗？",
        "answer": "运动鞋清洗方法：\n1. 先用软毛刷清除表面灰尘\n2. 用温和的洗涤剂和温水清洗\n3. 避免机洗和漂白\n4. 自然晾干，避免阳光直射",
        "category": "测试分类"
    }
    
    try:
        response = requests.post(f"{base_url}/api/qa", json=test_qa)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                logger.info("✓ 问答对添加成功")
            else:
                logger.error(f"✗ 问答对添加失败: {result.get('message')}")
        else:
            logger.error(f"✗ 问答管理接口异常: {response.status_code}")
            
    except Exception as e:
        logger.error(f"✗ 问答管理测试失败: {e}")

def test_batch_query():
    """测试批量查询功能"""
    base_url = "http://localhost:8000"
    
    logger.info("开始测试批量查询功能...")
    
    # 测试批量查询
    batch_queries = [
        {"query": "篮球鞋品牌推荐", "user_id": "test_user"},
        {"query": "护膝尺寸选择", "user_id": "test_user"},
        {"query": "跑步机保养方法", "user_id": "test_user"}
    ]
    
    try:
        response = requests.post(f"{base_url}/api/batch-query", json=batch_queries)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                logger.info(f"✓ 批量查询成功，处理了{len(batch_queries)}个查询")
            else:
                logger.error(f"✗ 批量查询失败: {result.get('message')}")
        else:
            logger.error(f"✗ 批量查询接口异常: {response.status_code}")
            
    except Exception as e:
        logger.error(f"✗ 批量查询测试失败: {e}")

def test_hot_queries():
    """测试热门查询功能"""
    base_url = "http://localhost:8000"
    
    logger.info("开始测试热门查询功能...")
    
    try:
        response = requests.get(f"{base_url}/api/hot-queries?limit=5")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                hot_queries = result['data'].get('hot_queries', [])
                logger.info(f"✓ 热门查询获取成功，共{len(hot_queries)}个")
            else:
                logger.error(f"✗ 热门查询获取失败: {result.get('message')}")
        else:
            logger.error(f"✗ 热门查询接口异常: {response.status_code}")
            
    except Exception as e:
        logger.error(f"✗ 热门查询测试失败: {e}")

def test_error_handling():
    """测试错误处理"""
    base_url = "http://localhost:8000"
    
    logger.info("开始测试错误处理...")
    
    # 测试空查询
    try:
        response = requests.post(f"{base_url}/api/query", json={
            "query": "",
            "user_id": "test_user"
        })
        
        if response.status_code == 422:  # 验证错误
            logger.info("✓ 空查询验证正常")
        else:
            logger.warning(f"⚠ 空查询处理异常: {response.status_code}")
            
    except Exception as e:
        logger.error(f"✗ 空查询测试失败: {e}")
    
    # 测试超长查询
    try:
        long_query = "测试" * 300  # 超过1000字符限制
        response = requests.post(f"{base_url}/api/query", json={
            "query": long_query,
            "user_id": "test_user"
        })
        
        if response.status_code == 422:  # 验证错误
            logger.info("✓ 超长查询验证正常")
        else:
            logger.warning(f"⚠ 超长查询处理异常: {response.status_code}")
            
    except Exception as e:
        logger.error(f"✗ 超长查询测试失败: {e}")

def run_performance_test():
    """运行性能测试"""
    base_url = "http://localhost:8000"
    
    logger.info("开始性能测试...")
    
    # 测试响应时间
    test_query = "篮球鞋怎么选择？"
    response_times = []
    
    for i in range(5):
        try:
            start_time = time.time()
            response = requests.post(f"{base_url}/api/query", json={
                "query": test_query,
                "user_id": f"perf_user_{i}",
                "session_id": f"perf_session_{i}"
            })
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = end_time - start_time
                response_times.append(response_time)
                logger.info(f"第{i+1}次测试响应时间: {response_time:.3f}s")
            else:
                logger.error(f"第{i+1}次测试失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"第{i+1}次测试异常: {e}")
        
        time.sleep(1)
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        logger.info(f"性能测试结果:")
        logger.info(f"  平均响应时间: {avg_time:.3f}s")
        logger.info(f"  最快响应时间: {min_time:.3f}s")
        logger.info(f"  最慢响应时间: {max_time:.3f}s")

def main():
    """主测试函数"""
    logger.info("=" * 50)
    logger.info("体育用品电商AI客服RAG系统测试开始")
    logger.info("=" * 50)
    
    try:
        # 等待服务启动
        logger.info("等待服务启动...")
        time.sleep(5)
        
        # 运行各项测试
        test_api_endpoints()
        time.sleep(2)
        
        test_query_functionality()
        time.sleep(2)
        
        test_qa_management()
        time.sleep(2)
        
        test_batch_query()
        time.sleep(2)
        
        test_hot_queries()
        time.sleep(2)
        
        test_error_handling()
        time.sleep(2)
        
        run_performance_test()
        
        logger.info("=" * 50)
        logger.info("所有测试完成！")
        logger.info("=" * 50)
        
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    main()


