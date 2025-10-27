"""
测试日志系统修复
"""
from flask import Flask, g
from utils.logger import get_logger, add_request_id_to_context, CustomFormatter
import uuid
import logging


def test_logging_with_request_id():
    """测试带有request_id的日志记录"""
    app = Flask(__name__)
    
    with app.app_context():
        # 模拟请求上下文并添加请求ID
        with app.test_request_context():
            add_request_id_to_context()  # 添加请求ID到上下文
            
            # 测试格式化器
            formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s - [Request-ID: %(request_id)s] - %(message)s')
            
            # 获取logger并记录日志
            logger = get_logger(__name__)
            
            request_id = getattr(g, 'request_id', 'N/A')
            print(f"Generated request_id: {request_id}")
            
            logger.info("This is an info message with request_id")
            logger.warning("This is a warning message with request_id")
            logger.error("This is an error message with request_id")
            
            # 测试SQLAlchemy日志
            from utils.logger import setup_sqlalchemy_logger
            setup_sqlalchemy_logger()
            sql_logger = logging.getLogger('sqlalchemy.engine')
            sql_logger.info("This is a SQL log message with request_id")


def test_without_request_context():
    """测试在没有请求上下文的情况下记录日志"""
    # 直接使用logger，不添加请求上下文
    logger = get_logger(__name__)
    logger.info("This is a message without request context")
    print("Message without context logged successfully")


def test_unique_request_ids():
    """测试不同请求是否生成不同的请求ID"""
    app = Flask(__name__)
    
    request_ids = []
    
    with app.app_context():
        for i in range(5):
            with app.test_request_context():
                add_request_id_to_context()
                request_id = getattr(g, 'request_id', 'N/A')
                request_ids.append(request_id)
                logger = get_logger(f"test_{i}")
                logger.info(f"Test log message for request {request_id}")
    
    print("Generated request IDs:", request_ids)
    print("All IDs unique:", len(request_ids) == len(set(request_ids)))


if __name__ == "__main__":
    print("Testing logging system with request_id...")
    test_logging_with_request_id()
    print("\nTesting logging without request context...")
    test_without_request_context()
    print("\nTesting unique request IDs...")
    test_unique_request_ids()
    print("\nLogging system test completed successfully!")