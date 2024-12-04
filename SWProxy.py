# !/usr/bin/env python3.7
# coding=utf-8
import asyncio
import random
import string
import traceback
from pathlib import Path
from time import time
from lib.Log import logger
from lib.Conf import config
from mitmproxy import http, options
from mitmproxy.tools.dump import DumpMaster
from beans.SWProxyBean import SWProxyBean
from ProxyMatch import replace_reqdata, replace_rspdata, store_data


class ScheduleProxy:
    """
    代理功能
    1. 支持http、https、ws、wss等代理
    2. 支持对特定http流进行修改，包括url、请求头、请求体、响应头、响应体
    3. 支持对特定http流进行存储
    TODO 当前使用关系型数据库，可能遇到性能问题
    """

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.db = SWProxyBean()
        self.config = config.httpproxy
        self.coding = self.config.get("coding") if self.config.get("coding") else config.getcode()
        self.block_global = False
        self.datas = list()
        self.time = time()

    def deal_data(self):
        """
        统一处理实时结果，自定义存储条件(大于多少条数据，大于多长时间)
        """
        try:
            if len(self.datas) > self.config.get("maxnum"):
                self.db.insert_many(self.datas)
                self.datas = list()
                return True
            now = time()
            if now - self.time > self.config.get("timestamp"):
                self.db.insert_many(self.datas)
                self.datas = list()
                self.time = now
                return True
            return False
        except:
            logger.error(f"数据处置异常：{traceback.format_exc()}")

    def request(self, flow: http.HTTPFlow):
        """
        处理请求数据
        :param flow: 数据流
        :return:
        """
        try:
            url, reqheaders, reqbody = replace_reqdata(flow.request.url.encode("ascii"), flow.request.headers,
                                                       flow.request.get_content())
            flow.request.url = url
            flow.request.headers = reqheaders
            flow.request.content = reqbody
        except:
            logger.error(f"请求替换失败：{traceback.format_exc()}")

    def response(self, flow: http.HTTPFlow):
        """
        处理响应数据
        :param flow: 数据流
        :return:
        """
        try:
            rspheaders, rspbody = replace_rspdata(flow.response.headers, flow.response.get_content())
            flow.response.headers = rspheaders
            flow.response.content = rspbody
            store_data(self.datas, self.task_id, flow.request.method, flow.request.url, flow.request.headers,
                       flow.request.get_content(),
                       flow.response.http_version, flow.response.status_code, flow.response.reason,
                       flow.response.headers,
                       flow.response.get_content())
            self.deal_data()
        except:
            logger.error(f"响应处置失败：{traceback.format_exc()}")

    def http_connect(self, flow: http.HTTPFlow):
        # 处理客户端发起的连接
        try:
            return
        except:
            logger.error(f"http连接处理失败：{traceback.format_exc()}")

    def done(self):
        """
        统一处理deal_data没有处理完的数据
        """
        self.db.insert_many(self.datas)
        logger.info(f"{self.task_id}, bye~")


async def start_server(task_id, proxy_mode=None):
    if proxy_mode is None or ['http']:
        proxy_mode = ["regular"]
    proxy_host = config.httpproxy.get("proxyserver", "0.0.0.0")
    proxy_port = config.httpproxy.get("proxyport", "10800")
    opts = options.Options(
        listen_host=proxy_host,
        listen_port=proxy_port,
        mode=[proxy_mode[0]]
    )
    opts.add_option("body_size_limit", int, 0, "")
    opts.add_option("keep_host_header", bool, True, "")
    certpath = config.globalvar.get("swpem")
    certpath = certpath if certpath else f"{Path.home()}/.mitmproxy/mitmproxy-ca.pem"
    opts.add_option("cert", str, certpath, "Specify path to the certificate file")
    m = DumpMaster(opts)
    m.addons.add(ScheduleProxy(task_id))
    # 禁用 block_global 选项
    m.options.set('block_global=false')
    await m.run()


def main(taskid=None):
    if taskid is None:
        taskid = "".join(random.sample(string.ascii_lowercase + string.digits * 2, 10))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server(taskid))


if __name__ == "__main__":
    main()
