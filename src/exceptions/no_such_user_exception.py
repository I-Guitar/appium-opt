"""
Created by joe on 2019/6/17
"""
from selenium.common.exceptions import NoSuchElementException


class NoSuchUserException(NoSuchElementException):
    """找不到用户异常"""
