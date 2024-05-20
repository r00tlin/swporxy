# !/usr/bin/env python3.7
# coding=utf-8

import re, os
import json
import sys
import traceback
import importlib

import mitmproxy.http

from lib.Log import logger
from lib.Conf import config
from copy import deepcopy
from lib.StrUtils import byte_to_str
from beans.SWProxyBean import SWProxy_Record, SWProxyBean

CONFIG = config.httpproxy
CODING = CONFIG.get("coding") if CONFIG.get("coding") else config.getcode()


def get_rules():
    try:
        with open(os.path.join(config.rootpath, CONFIG.get("rulepath")), "r",
                  encoding=CODING) as fp:
            data = json.load(fp)
            return data.get("replace"), data.get("store")
    except:
        logger.error(f"无法正常获取规则内容，错误详情:{traceback.format_exc()}")


def encode_rule(rule) -> bytes:
    return b"|".join([rule.encode(CODING), rule.encode("unicode-escape").replace(b"\\", b"\\\\")])


def match_data(rule, data, newdata, count=1, ignorecase=True):
    """
    正则匹配并替换字符
    :param rule: 替换规则
    :param data: 原始数据
    :param newdata: 替换为的值
    :param count: 替换个数
    :param ignorecase: 是否忽略大小写
    :return: 替换后的数据
    """
    ignorecase = re.IGNORECASE if ignorecase else 0
    return re.sub(rule, newdata, data, count=count, flags=ignorecase)


def replace_reqdata(url, reqheader, reqbody):
    """
    根据httpproxy.json中的配置规则来替换
    :param url: 请求url,字节形式
    :param reqheader: 请求头数据，字节字典形式
    :param reqbody: 请求体数据，字节形式
    :return: 替换后的结果，为字节tuple形式：(url, reqheader, reqbody)
    """
    rules = get_rules()[0]
    if rules:
        for rule in rules:
            script = rule.get("script")
            if not script:
                point = rule.get("point")  # 需要替换的点
                if point not in {"url", "reqheader", "reqbody"}:
                    break
                replace = rule.get("replace").encode(CODING)  # 替换以后的数据
                count = rule.get("count")  # 替换个数
                ignorecase = rule.get("ignorecase")  # 是否忽略大小写
                match = encode_rule(rule.get("match"))  # 需要替换的数据，支持正则表达式
                if point == "url":
                    url = match_data(match, url, replace, count, ignorecase)
                elif point == "reqheader":
                    temp = deepcopy(reqheader)
                    for key, value in temp.items():
                        key = key.encode(CODING)
                        value = value.encode(CODING)
                        tdata = key + b": " + value
                        rdata = match_data(match, tdata, replace, count, ignorecase)
                        loc = rdata.find(b":")
                        if loc != -1:
                            reqheader.pop(key)
                            reqheader[rdata[:loc].strip()] = rdata[loc + 1:].strip()
                elif point == "reqbody" and reqbody:
                    reqbody = match_data(match, reqbody, replace, count, ignorecase)
            else:
                try:
                    import_class = getattr(importlib.import_module(f"scripts.{script}"),
                                           "SwProxy")(url=url, reqheader=reqheader, reqbody=reqbody)
                    import_class.deal_req()
                    url, reqheader, reqbody = import_class.url, import_class.reqheader, import_class.reqbody
                except:
                    logger.error(f"导入{script}.py代理脚本错误，细节：{traceback.format_exc()}")
    return url, reqheader, reqbody


def replace_rspdata(rspheader, rspbody):
    """
    根据httpproxy.json中配置规则来替换
    :param rspheader: 响应头，字节字典形式
    :param rspbody: 响应体，字节形式
    :return: 替换后的结果，rspbody
    """
    rules = get_rules()[0]
    if rules:
        for rule in rules:
            script = rule.get("script")
            if not script:
                point = rule.get("point")  # 需要替换的点
                if point not in {"rspheader", "rspbody"}:
                    break
                count = rule.get("count")  # 替换个数
                ignorecase = rule.get("ignorecase")  # 是否忽略大小写
                match = encode_rule(rule.get("match"))  # 需要替换的数据，支持正则表达式
                replace = rule.get("replace").encode(CODING)  # 替换以后的数据
                if point == "rspheader":
                    temp = deepcopy(rspheader)
                    for key, value in temp.items():
                        key = key.encode(CODING)
                        value = value.encode(CODING)
                        tdata = key + b": " + value
                        rdata = match_data(match, tdata, replace, count, ignorecase)
                        loc = rdata.find(b":")
                        if loc != -1:
                            rspheader.pop(key)
                            rspheader[rdata[:loc].strip()] = rdata[loc + 1:].strip()
                elif point == "rspbody" and rspbody:
                    rspbody = match_data(match, rspbody, replace, count, ignorecase)
            else:
                try:
                    import_class = getattr(importlib.import_module(f"scripts.{script}"),
                                           "SwProxy")(url=None, rspheader=rspheader, rspbody=rspbody)
                    import_class.deal_rsp()
                    rspheader, rspbody = import_class.rspheader, import_class.rspbody
                except:
                    logger.error(f"导入{script}.py代理脚本错误，细节：{traceback.format_exc()}")
    return rspheader, rspbody


def check_data(rule: bytes, data: bytes, count: int, ignorecase=True):
    if data:
        count = count if count else 1
        ignorecase = re.IGNORECASE if ignorecase else 0
        if len(re.findall(rule, data, flags=ignorecase)) >= count:
            return True
        else:
            return False
    else:
        return False


def create_data(store: SWProxy_Record):
    length = CONFIG.get("maxlength", 1024)
    if length > 0:
        if store.reqbody:
            store.reqbody = store.reqbody[: length]
        if store.rspbody:
            store.rspbody = store.rspbody[: length]


def store_data(db: list[SWProxy_Record], taskid: str, method: str, url: str, reqheader: mitmproxy.http.Headers,
               reqbody: bytes,
               proto: str, code: int, reason: str, rspheader: mitmproxy.http.Headers, rspbody: bytes):
    """
    根据请求响应匹配需要的数据，并进行存储
    :param db: 数据库类
    :param taskid: 任务ID
    :param method: http方法， 字符形式
    :param url: 请求地址, 字节串形式
    :param reqheader: 请求头，字节字典形式
    :param reqbody: 请求体， 字节串形式
    :param proto: 协议版本， 字符形式
    :param code: 状态码， 整数形式
    :param reason: 应答提示， 字符形式
    :param rspheader: 响应头， 字节字典形式
    :param rspbody: 响应体， 字节串形式
    :return: bool
    """
    rules = get_rules()[1]
    if rules:
        for rule in rules:
            ruleid = rule.get("id")
            script = rule.get("script")
            if not script:
                point = rule.get("point")  # 需要存储的点
                store = rule.get("store")  # 需要存储的数据
                count = rule.get("count")  # 正则匹配到的个数
                ignorecase = rule.get("ignorecase")  # 是否忽略大小写
                match = encode_rule(rule.get("match"))  # 需要满足的条件，支持正则表达式
                crossrow = rule.get("crossrow")
                temp = byte_to_str({
                    "taskid": taskid,
                    "ruleid": ruleid,
                    "method": method,
                    "reqheader": dict(reqheader),
                    "reqbody": reqbody,
                    "code": code,
                    "reason": reason,
                    "rspheader": dict(rspheader),
                    "rspbody": rspbody,
                    "proto": proto,
                    "url": url,
                }, CODING)
                if store == "all":
                    stores = SWProxy_Record(**temp)
                else:
                    stores = SWProxy_Record(taskid, ruleid, None, None, None, None, None, None, None, None, None)
                    for s in store.split("|"):
                        if s == "url":
                            stores.url = temp.get("url")
                        elif s == "method":
                            stores.method = temp.get("method")
                        elif s == "reqheader":
                            stores.reqheader = temp.get("reqheader")
                        elif s == "reqbody":
                            stores.reqbody = temp.get("reqbody")
                        elif s == "code":
                            stores.code = temp.get("code")
                        elif s == "reason":
                            stores.reason = temp.get("reason")
                        elif s == "rspheader":
                            stores.rspheader = temp.get("rspheader")
                        elif s == "rspbody":
                            stores.rspbody = temp.get("rspbody")
                        elif s == "proto":
                            stores.proto = temp.get("proto")
                if point == "url":
                    if check_data(match, url.encode(CODING), count, ignorecase):
                        create_data(stores)
                        db.append(stores)
                elif point == "reqheader":
                    if check_data(match, b"\r\n".join(
                            [key.encode(CODING) + b": " + value.encode(CODING) for key, value in reqheader.items()]),
                                  count,
                                  ignorecase):
                        create_data(stores)
                        db.append(stores)
                elif point == "reqbody" and reqbody:
                    tmp = reqbody
                    if crossrow:
                        tmp = tmp.replace(b"\r\n", b"").replace(b"\n", b"")
                    if check_data(match, tmp, count, ignorecase):
                        create_data(stores)
                        db.append(stores)
                elif point == "rspheader":
                    if check_data(match, b"\r\n".join(
                            [key.encode(CODING) + b": " + value.encode(CODING) for key, value in rspheader.items()]),
                                  count,
                                  ignorecase):
                        create_data(stores)
                        db.append(stores)
                elif point == "rspbody" and rspbody:
                    tmp = rspbody
                    if crossrow:
                        tmp = tmp.replace(b"\r\n", b"").replace(b"\n", b"")
                    if check_data(match, tmp, count, ignorecase):
                        create_data(stores)
                        db.append(stores)
            else:
                try:
                    result = getattr(importlib.import_module(f"scripts.{script}"), "SwProxy")(
                        taskid=taskid,
                        ruleid=ruleid,
                        method=method,
                        url=url,
                        reqheader=dict(reqheader),
                        reqbody=reqbody,
                        proto=proto,
                        reason=reason,
                        code=code,
                        rspheader=dict(rspheader),
                        rspbody=rspbody).deal_store()
                    if result:
                        create_data(result)
                        db.append(result)
                except:
                    logger.error(f"导入{script}.py代理脚本错误，细节：{traceback.format_exc()}")
