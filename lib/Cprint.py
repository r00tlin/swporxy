# !/usr/bin/env python3.7
# coding=utf-8
# Date: 2024/5/16
# Description: 
"""
终端色彩输出
"""

from colorama import init, Fore

init(autoreset=True)


def setcolor(string, kind):
    """
    设置输出颜色
    :param string: 原始字符
    :param kind: 颜色
    :return:
    """
    if kind == 1:
        # 红色输出
        return Fore.RED + string
    elif kind == 2:
        # 绿色输出
        return Fore.GREEN + string
    elif kind == 3:
        # 黄色输出
        return Fore.YELLOW + string
    elif kind == 4:
        # 蓝色输出
        return Fore.BLUE + string
    elif kind == 5:
        # 黑色输出
        return Fore.BLACK + string
    else:
        # 默认白色输出
        return Fore.WHITE + string
