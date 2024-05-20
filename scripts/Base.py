# !/usr/bin/env python3.7
# coding=utf-8
from typing import Dict
from lib.Conf import config
from lib.StrUtils import byte_to_str
from beans.SWProxyBean import SWProxy_Record


class Base:
    def __init__(self, url: str = "", reqheader: Dict[bytes, bytes] = None, reqbody: bytes = b'', decode=None,
                 taskid: str = "",
                 ruleid: str = "", method: str = "", proto: str = "", reason: str = "",
                 code: int = 0,
                 rspheader: Dict[bytes, bytes] = None, rspbody: bytes = b""):
        """
        所有脚本需要继承的父类, 子类的类名必须保证为SwProxy
        :param taskid: 任务ID, eg：8fc22ba09913faa3
        :param ruleid: 规则ID, eg：1
        :param method: 请求方式, eg：GET
        :param url: 请求url
        :param reqheader/rspheader: 请求头/响应头, 字节字典类型，eg：{b"host": b"www.example.com"}
        :param reqbody/rspbody: 请求体/响应体, 字节串类型，eg：b"example"
        :param proto: 协议版本, eg：HTTP/2
        :param reason: 响应描述, 200 OK里面的OK
        :param code: 请求端口
        """
        self.taskid = taskid
        self.ruleid = ruleid
        self.method = method
        self.url = url
        self.reqheader = reqheader
        self.reqbody = reqbody
        self.proto = proto
        self.reason = reason
        self.code = code
        self.rspheader = rspheader
        self.rspbody = rspbody

        # 私有属性，不做输出
        self.__CONFIG = config.httpproxy
        self.__CODING = decode if decode else self.__CONFIG.get("coding") if self.__CONFIG.get(
            "coding") else config.getcode()

    def deal_req(self):
        # 处理请求数据方法，不强制必须返回值self.url, self.reqheader, self.reqbody
        return None

    def deal_rsp(self):
        # 处理响应数据方法，不强制必须返回值self.rspheader, self.rspbody
        return None

    def standard(self) -> dict:
        # 将所有非私有的属性格式化
        params = {_k: _v for _k, _v in vars(self).items() if not _k.startswith("_Base")}
        return byte_to_str(params, self.__CODING)

    def deal_store(self) -> SWProxy_Record:
        # 处理存储数据
        # 必须实现
        return SWProxy_Record(**self.standard())
