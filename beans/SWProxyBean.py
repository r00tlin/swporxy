# !/usr/bin/env python3.7
# coding=utf-8
# Date: 2024/5/16
# Description: 
"""

"""
from datetime import datetime

# !/usr/bin/env python3.7
# coding=utf-8
# Date: 2023/9/7
# Description:
"""
代理结果存储
TODO 后续也可以考虑放到ES中
"""

from beans import *
from beans.SQLBean import SQLBean


class SWProxy_Record(Base_table, Base):
    # 表的名字:
    __tablename__ = 'sw_proxy_record'

    # 表的结构:
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    taskid = Column(CHAR(16), comment='任务ID')
    ruleid = Column(INT, comment='规则ID')
    method = Column(CHAR(10), nullable=True, comment='请求方式')
    url = Column(TEXT, nullable=True, comment='url')
    reqheader = Column(JSON, nullable=True, comment='请求头')
    reqbody = Column(Text, nullable=True, comment='请求体')
    proto = Column(TEXT, nullable=True, comment='响应中的HTTP协议')
    code = Column(INT, nullable=True, comment='状态码')
    reason = Column(TEXT, nullable=True, comment='状态标识')
    rspheader = Column(JSON, nullable=True, comment='响应头')
    rspbody = Column(Text(length=4294967295), nullable=True, comment='响应体')

    def __init__(self, taskid: str, ruleid: int, method: str, url: str, reqheader: dict, reqbody: str, proto: str,
                 code: int, reason: str, rspheader: dict, rspbody: str, create_time=None, update_time=None):
        super().__init__()
        self.taskid = taskid
        self.ruleid = ruleid
        self.method = method
        self.url = url
        self.reqheader = reqheader
        self.reqbody = reqbody
        self.proto = proto
        self.code = code
        self.reason = reason
        self.rspheader = rspheader
        self.rspbody = rspbody
        self.create_time = create_time if create_time else datetime.now()
        self.update_time = update_time if update_time else datetime.now()


class SWProxyBean(SQLBean):
    def __init__(self):
        super().__init__()
        self.table = SWProxy_Record
