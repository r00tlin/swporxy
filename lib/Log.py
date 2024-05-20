# !/usr/bin/env python3.7
# coding=utf-8
# Date: 2024/5/16
# Description: 
"""
日志打印
"""
import os
import logging
import traceback
from lib.Cprint import setcolor
from lib.Projpath import rootpath


class Log:
    """
    日志生成
    """

    def __init__(self, name=""):
        self.cpath = rootpath
        if not os.path.exists(os.path.join(self.cpath, "logs")):
            os.mkdir(os.path.join(self.cpath, "logs"))

    def base(self, path, level):
        logman = logging.getLogger()
        filename, lineno, _, _ = logging.getLogger('').findCaller()
        Format = f"%(levelname)s - %(asctime)s - <PID:%(process)s/TID:%(thread)s> - {filename}:{lineno} - " \
                 f"Details: %(message)s "
        handlers = logging.FileHandler(filename=path, encoding="utf-8")
        handlers.setFormatter(logging.Formatter(Format))
        logman.handlers = [handlers]
        logman.setLevel(level)
        return logman

    def debug(self, msg, filename="debug.log"):
        try:
            path = os.path.join(self.cpath, "logs", filename)
            log = self.base(path, logging.DEBUG)
            log.debug(msg)
        except:
            print(setcolor("(严重错误)日志文件info.log记录出错，请查看详细内容：", 1))
            traceback.print_exc()

    def info(self, msg, filename="info.log"):
        try:
            path = os.path.join(self.cpath, "logs", filename)
            log = self.base(path, logging.INFO)
            log.info(msg)
        except:
            print(setcolor("(严重错误)日志文件info.log记录出错，请查看详细内容：", 1))
            traceback.print_exc()

    def warn(self, msg, filename="info.log"):
        try:
            path = os.path.join(self.cpath, "logs", filename)
            log = self.base(path, logging.WARN)
            log.warning(msg)
        except:
            print(setcolor("(严重错误)日志文件info.log记录出错，请查看详细内容：", 1))
            traceback.print_exc()

    def error(self, msg, filename="error.log"):
        try:
            path = os.path.join(self.cpath, "logs", filename)
            log = self.base(path, logging.ERROR)
            log.error(msg)
        except:
            print(setcolor("(严重错误)日志文件error.log记录出错，请查看详细内容：", 1))
            traceback.print_exc()

    def critical(self, msg, filename="critical.log"):
        try:
            path = os.path.join(self.cpath, "logs", filename)
            log = self.base(path, logging.CRITICAL)
            log.critical(msg)
        except:
            print(setcolor("(致命错误)日志文件error.log记录出错，请查看详细内容：", 1))
            traceback.print_exc()

    def security(self, msg, filename="security.log"):
        # 对可能造成安全问题的地方，进行打点日志
        try:
            path = os.path.join(self.cpath, "logs", filename)
            log = self.base(path, logging.CRITICAL)
            log.critical(msg)
        except:
            print(setcolor("(致命错误)日志文件security.log记录出错，请查看详细内容：", 1))
            traceback.print_exc()


logger = Log()
