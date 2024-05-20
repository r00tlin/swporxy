# !/usr/bin/env python3.7
# coding=utf-8
# Date: 2024/5/16
# Description:
import os.path
import sys
import yaml
import traceback
from lib.Log import Log
from lib.Cprint import setcolor
from lib.Projpath import rootpath


class Conf:
    """
    配置类
    """
    def __init__(self, filename=os.path.join(rootpath, "config.yaml"), encoding="utf-8"):
        try:
            with open(filename, "r", encoding=encoding) as fp:
                self.rootpath = rootpath
                self.confs = yaml.safe_load(fp.read())
                self.globalvar = self.confs.get("global")
                self.httpproxy = self.confs.get("httpproxy")
                self.platform = sys.platform if sys.platform else "unknown"
        except:
            Log(__name__).critical(f"严重错误！配置文件无法导入,报错信息{traceback.format_exc()}")
            print(setcolor("配置文件无法读取，详情请查看error.log信息！", 1))

    def getcode(self, section=None):
        # 获取项目编码
        if section:
            return self.confs.get(section).get("coding")
        else:
            return self.globalvar.get("coding")


config = Conf()