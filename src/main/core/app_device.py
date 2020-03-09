"""
Created by joe on 2019/10/29

基于 Appnium 的 app 操作
"""
import base64
import logging
import os
import re
import time

from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conf.config import APPNIUM_SERVER
from src.main.exceptions.miss_param_exception import MissParamException
from src.main.exceptions.tap_failed_exception import TapFailedException

logger = logging.getLogger("AppDevice")


class AppDevice(object):
    """app device"""

    def __init__(self, platform_name, device_name, app_package, app_activity, wait_time=10):
        """
        初始化
        :param platform_name: 平台名（Android / IOS）
        :param device_name: 设备名
        :param app_package: app package
        :param app_activity: app activity
        :param wait_time: 选择元素时等待时间，默认为10秒
        """
        if not (platform_name and device_name and app_package and app_activity):
            raise MissParamException("app opt initial failed!")

        self.__platform_name = platform_name
        self.__device_name = device_name
        self.__app_package = app_package
        self.__app_activity = app_activity

        desired_caps = {
            "platformName": platform_name,
            "deviceName": device_name,
            "appPackage": app_package,
            "appActivity": app_activity
        }
        self.__driver = webdriver.Remote(APPNIUM_SERVER, desired_caps)
        self.__driver_wait = WebDriverWait(self.__driver, wait_time)

    def tap(self, positions, duration=None, delay=None):
        """
        指定位置点击
        :param positions: 位置数组 [(100, 20), (100, 60), (100, 100)]
        :param duration: 间隔
        :param delay: 延迟点击
        :return:
        """
        if delay:
            time.sleep(delay)

        self.__driver.tap(positions, duration)

    def tap_and_wait_for(self, positions, duration=None, delay=None, id_name=None, class_name=None, label_text=None,
                         retry=3):
        """
        点击后等待元素加载
        :param positions: 点击位置
        :param duration: 点击时间间隔
        :param delay: 延迟点击
        :param id_name: id
        :param class_name: class
        :param label_text: 标签文本
        :param retry: 重试次数
        :return:
        """
        if not (id_name or class_name):
            raise MissParamException("You must choose at least one id_name or class_name.")

        failed = 0
        while failed < retry:
            self.tap(positions, duration, delay)
            if self.wait_for(id_name=id_name, class_name=class_name, label_text=label_text):
                logger.info("Tap successfully! positions -> {0}".format(positions))
                return
            failed += 1

        raise TapFailedException("Tap failed! positions -> {0}".format(positions))

    def wait_for(self, id_name=None, class_name=None, label_text=None, wait_time=None):
        """
        等待页面中元素加载
        :param id_name: id 和 class 必须有其中一个
        :param class_name:
        :param label_text: 标签文本
        :param wait_time: 等待时间
        :return: 是否等到了
        """
        has_found = False
        if not (id_name or class_name):
            raise MissParamException("You must choose at least one id_name or class_name.")

        element = None
        if id_name:
            element = self.find_element_by_id(id_name, wait_time=wait_time)
        elif class_name:
            element = self.find_element_by_class(class_name, wait_time=wait_time)

        if element:
            if label_text and element.text != label_text:
                has_found = False
            else:
                has_found = True

        return has_found

    def find_element_by_id(self, element_id, wait=True, wait_time=None):
        """
        通过 id 查找匹配的单个元素
        :param element_id: element id
        :param wait: 选择元素是否等待，默认为等待，等待时长初始化时设置
        :param wait_time:
        :return: element or None
        """
        element = None
        driver_wait = self.__driver_wait
        if wait_time:
            driver_wait = WebDriverWait(self.__driver, wait_time)
        try:
            if wait:
                element = driver_wait.until(EC.presence_of_element_located((By.ID, element_id)))
            else:
                element = self.__driver.find_element_by_id(element_id)
        except Exception as _:
            logger.warning("find element by id failed! ")
        return element

    def find_elements_by_id(self, element_id, wait=True, wait_time=None):
        """
        通过 id 查找匹配的所有元素
        :param element_id:
        :param wait:
        :param wait_time:
        :return:
        """
        results = None
        driver_wait = self.__driver_wait
        if wait_time:
            driver_wait = WebDriverWait(self.__driver, wait_time)
        try:
            if wait:
                results = driver_wait.until(EC.presence_of_all_elements_located((By.ID, element_id)))
            else:
                results = self.__driver.find_elements_by_id(element_id)
        except Exception as _:
            logger.warning("find elements by id failed! ")
        return results

    def find_element_by_class(self, element_class, wait=True, wait_time=None):
        """
        通过 class name 查找匹配的单个元素
        :param element_class:
        :param wait:
        :param wait_time:
        :return:
        """
        results = None
        driver_wait = self.__driver_wait
        if wait_time:
            driver_wait = WebDriverWait(self.__driver, wait_time)
        try:
            if wait:
                results = driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, element_class)))
            else:
                results = self.__driver.find_element_by_class_name(element_class)
        except Exception as __e:
            logger.warning("find element by class failed! ")
        return results

    def find_elements_by_class(self, element_class, wait=True, wait_time=None):
        """
        通过 class name 查找匹配的所有元素
        :param element_class:
        :param wait:
        :param wait_time:
        :return:
        """
        results = None
        driver_wait = self.__driver_wait
        if wait_time:
            driver_wait = WebDriverWait(self.__driver, wait_time)
        try:
            if wait:
                results = driver_wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, element_class)))
            else:
                results = self.__driver.find_elements_by_class_name(element_class)
        except Exception as __e:
            logger.warning("find elements by class failed! ")
        return results

    def find_element_by_path_tree(self, path_tree, wait=True, wait_time=None):
        """
        路径查找单个元素，语法风格 => #apro>.text>input[4]
        FIXME beta方法，未充分考虑所有情况。使用需谨慎
        :param path_tree:
        :param wait:
        :param wait_time:
        :return:
        """
        element = self.find_elements_by_path_tree(path_tree, wait, wait_time)
        if element:
            return element[0]
        return None

    def find_elements_by_path_tree(self, path_tree, wait=True, wait_time=None):
        """
        路径查找所有元素，语法风格 => #apro>.text>input[4]
        FIXME beta方法，未充分考虑所有情况。使用需谨慎
        :param path_tree:
        :param wait:
        :param wait_time:
        :return:
        """
        element = None
        selects = re.split("[\s+>]", path_tree)
        sel_len = len(selects)

        for i in range(sel_len):
            sel = selects[i]
            position = None

            if re.match(".*?\[\d+]$", sel):
                index = sel.rindex("[")
                position = sel[index + 1:len(sel) - 1]
                sel = sel[:index]

            if sel.startswith("#"):
                sel = sel[1:]
                if not element:
                    element = self.find_elements_by_id(sel, wait, wait_time)
                else:
                    element = element.find_elements_by_id(sel)
            elif sel.startswith("."):
                sel = sel[1:]
                if not element:
                    element = self.find_elements_by_class(sel, wait, wait_time)
                else:
                    element = element.find_elements_by_class_name(sel)

            if not element:
                return []

            if position:
                element = element[int(position)]  # FIXME 这里处理 下标越界异常（有滑块验证码导致的）

            if i < sel_len - 1 and isinstance(element, list):
                element = element[0]

        if not isinstance(element, list):
            return [element]
        return element

    def click_element_by_path_tree(self, path_tree, wait=True, wai_time=None):
        """
        路径查找，并点击，语法风格 => #apro>.text>input[4]
        FIXME beta方法，未充分考虑所有情况。使用需谨慎
        :param path_tree:
        :param wait:
        :param wai_time:
        :return:
        """
        element = self.find_element_by_path_tree(path_tree, wait, wai_time)
        if element:
            element.click()

    def click_element_by_id(self, element_id, wait=True, wait_time=None):
        """
        通过 id 点击元素
        :param element_id:
        :param wait:
        :param wait_time:
        :return:
        """
        element = self.find_element_by_id(element_id, wait, wait_time)
        if element:
            element.click()

    def click_element_by_class(self, element_class, wait=True, wait_time=None):
        """
        通过 class 点击元素
        :param element_class:
        :param wait:
        :param wait_time:
        :return:
        """
        element = self.find_element_by_class(element_class, wait, wait_time)
        if element:
            element.click()

    def press_key(self, key_code, times=1):
        """
        按下指定按键
        :param key_code: key code，参考 https://app.yinxiang.com/fx/7bd99348-e79e-431c-be68-19631f662095
        :param times: 次数
        :return: None
        """
        for i in range(times):
            self.__driver.press_keycode(key_code)

    def press_key_by_ime(self, ime_name, key_code, times=1):
        """
        使用指定输入法按下按键
        TODO 判断输入法是否成功启动
        :param ime_name: 输入法全称，查看方式 adb shell ime list -s
        :param key_code: 按键码 参考 https://app.yinxiang.com/fx/7bd99348-e79e-431c-be68-19631f662095
        :param times: 次数
        :return:
        """
        os.system("adb shell ime set {ime_name}".format(ime_name=ime_name))
        self.press_key(key_code, times)

    @staticmethod
    def swap_ime(ime_name):
        """
        切换输入法
        :param ime_name: 输入法全称，查看方式 adb shell ime list -s
        :return:
        """
        os.system("adb shell ime set {ime_name}".format(ime_name=ime_name))

    def send_keys_by_ADBKeyboard(self, keyword, id_name=None, class_name=None, wait=True, wait_time=None):
        """
        TODO 待修改，修改成使用adb输入内容，使用appnium输入
        TODO 输入法切换是否成功，判断。是否启动完毕
        向输入框中输入内容
        * id / class / xpath 至少需要给一个
        * 使用 adb 输入
        * 虚拟机中需要安装 ADBKeyboard https://github.com/senzhk/ADBKeyBoard
        :param keyword: 欲输入的文本
        :param id_name:
        :param class_name:
        :param wait:
        :param wait_time:
        :return:
        """
        os.system("adb shell ime set com.android.adbkeyboard/.AdbIME")
        if not (id_name or class_name):
            raise MissParamException("You must choose at least one id_name or class_name.")

        element = None
        if id_name:
            element = self.find_element_by_id(id_name, wait, wait_time)
        elif class_name:
            element = self.find_element_by_class(class_name, wait, wait_time)

        if element:
            element.click()
            encode_keyword = str(base64.b64encode(keyword.encode("utf-8")), "utf-8")
            os.system("adb -s {device} shell am broadcast -a ADB_INPUT_B64 --es msg \"{keyword}\"".format(
                device=self.__device_name,
                keyword=encode_keyword
            ))

    def swipe(self, start_position=None, end_position=None, times=1, duration=1000, delay=0, interval=0):
        """
        滚动屏幕
        :param start_position: 滑动起点坐标
        :param end_position: 滑动结束点坐标
        :param times: 滑动次数
        :param duration: 滑动时长
        :param delay: 延迟多久后开始滑动
        :param interval: 每次滑动的间隔
        :return:
        """
        if start_position is None:
            start_position = [600, 1200]
        if end_position is None:
            end_position = [600, 500]

        if delay > 0:
            time.sleep(delay)

        for index in range(times):
            self.__driver.swipe(start_position[0], start_position[1], end_position[0], end_position[1], duration)
            if interval > 0 and index < times - 1:
                time.sleep(interval)

    def close(self):
        """
        close
        :return:
        """
        self.__driver.close_app()
