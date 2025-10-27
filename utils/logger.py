"""
统一的日志记录工具，支持request_id
"""

import logging
import uuid
from flask import g
from functools import wraps
from contextvars import ContextVar
import threading
import contextvars


# 使用上下文变量来存储request_id
_request_id_var: ContextVar[str] = ContextVar("request_id", default="N/A")


class RequestIdFilter(logging.Filter):
    """为日志记录添加request_id的过滤器"""

    def filter(self, record):
        # 检查是否存在Flask g对象，如果存在且有request_id则使用它；否则使用contextvar
        context_request_id = _request_id_var.get()
        record.request_id = context_request_id
        return True


class CustomFormatter(logging.Formatter):
    """
    自定义格式化器，安全处理request_id字段
    """

    def format(self, record):
        # 确保record有request_id字段，如果没有则设置默认值
        context_request_id = _request_id_var.get()
        record.request_id = context_request_id

        return super().format(record)


def set_thread_request_id(request_id):
    """
    为当前线程设置request_id，以便在数据库操作等场景中使用
    """
    _request_id_var.set(request_id)


def get_current_request_id():
    """
    获取当前的request_id
    """
    return _request_id_var.get()


def copy_context_to_thread():
    """
    将当前上下文复制到新线程
    """
    return contextvars.copy_context()


def run_with_context(func, context=None):
    """
    在指定的上下文中运行函数
    """
    if context is None:
        context = contextvars.copy_context()
    return context.run(func)


def setup_sqlalchemy_logger():
    # print("set logging request_id: {}")
    """设置SQLAlchemy查询日志，确保SQL日志也包含request_id"""
    # 创建SQL日志记录器
    sql_logger = logging.getLogger("sqlalchemy.engine")

    # 添加request_id过滤器
    sql_logger.addFilter(RequestIdFilter())

    # 配置格式化程序
    if sql_logger.handlers:
        formatter = CustomFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - [Request-ID: %(request_id)s] - %(message)s"
        )
        for handler in sql_logger.handlers:
            handler.setFormatter(formatter)
    else:
        # 如果没有处理器，添加一个
        handler = logging.StreamHandler()
        formatter = CustomFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - [Request-ID: %(request_id)s] - %(message)s"
        )
        handler.setFormatter(formatter)
        sql_logger.addHandler(handler)

    sql_logger.setLevel(logging.INFO)

    return sql_logger


def get_logger(name):
    """获取一个带有request_id功能的日志记录器"""
    logger = logging.getLogger(name)

    # 为logger添加request_id过滤器
    if not any(isinstance(f, RequestIdFilter) for f in logger.filters):
        logger.addFilter(RequestIdFilter())

    # 仅在没有现有格式器时设置格式
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [Request-ID: %(request_id)s] - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    else:
        # 如果logger已经有处理器，为每个处理器重新设置格式化器
        formatter = CustomFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - [Request-ID: %(request_id)s] - %(message)s"
        )
        for handler in logger.handlers:
            handler.setFormatter(formatter)

    return logger


def log_api_call(func):
    """装饰器，记录API调用信息"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        request_id = getattr(g, "request_id", "N/A")
        logger.info(f"API Call: {func.__name__}, Request-ID: {request_id}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"API Call Success: {func.__name__}, Request-ID: {request_id}")
            return result
        except Exception as e:
            logger.error(
                f"API Call Failed: {func.__name__}, Error: {str(e)}, Request-ID: {request_id}"
            )
            raise

    return wrapper


def generate_request_id():
    """生成request_id"""
    return str(uuid.uuid4())


def add_request_id_to_context():
    """为当前请求设置request_id"""
    request_id = generate_request_id()
    g.request_id = request_id
    # 同时设置上下文变量
    _request_id_var.set(request_id)
