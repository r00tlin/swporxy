# !/usr/bin/env python3.7
# coding=utf-8
# Date: 2024/5/16
# Description: 
"""
路径获取
"""
from os import path

rootpath = f'{path.dirname(path.realpath(__file__)).split(".")[0]}/..'


def getpath(*args):
    return path.join(*[str(_).strip("/") for _ in args])
