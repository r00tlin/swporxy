# !/usr/bin/env python3.7
# coding=utf-8
# Date: 2024/5/16
# Description: 
"""
字符串处理
"""


def byte_to_str(data: dict, code):
    # 递归转换字节类型为字符类型
    # 编码这里为了统一都设置为了utf-8，这样也能保障入库没有异常
    # 如果去content-type可能会和数据库编码不匹配
    if isinstance(data, dict):
        char_dict = {}
        for key, value in data.items():
            char_key = key.decode(code, errors="ignore") if isinstance(key, bytes) else key
            char_value = byte_to_str(value, code)
            char_dict[char_key] = char_value
        return char_dict
    elif isinstance(data, list):
        char_list = []
        for item in data:
            char_item = byte_to_str(item, code)
            char_list.append(char_item)
        return char_list
    elif isinstance(data, bytes):
        return data.decode(code, errors="ignore")
    else:
        return data
