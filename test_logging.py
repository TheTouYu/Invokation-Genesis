"""
测试日志系统重构是否成功
"""
from flask import Flask, g
from utils.logger import get_logger, add_request_id_to_context
import uuid


def test_logging_with_request_id():
    """测试带有request_id的日志记录"""
    app = Flask(__name__)
    
    with app.app_context():
        # 模拟请求上下文并添加请求ID
        with app.test_request_context():
            add_request_id_to_context()  # 添加请求ID到上下文
            
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
            import logging
            sql_logger = logging.getLogger('sqlalchemy.engine')
            sql_logger.info("This is a SQL log message with request_id")


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
    print("\nTesting unique request IDs...")
    test_unique_request_ids()
    print("\nLogging system test completed successfully!")