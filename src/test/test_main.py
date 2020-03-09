"""
Created by joe on 2020/1/2

测试主函数
"""
import logging

from src.main.core.app_device import AppDevice

logger = logging.getLogger("AppDevice")

device = AppDevice("Android", "8c5670c7", "com.ss.android.ugc.aweme", ".splash.SplashActivity")
logger.info("app启动")
