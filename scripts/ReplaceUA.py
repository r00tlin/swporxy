# !/usr/bin/env python3.7
# coding=utf-8

from lib.Log import logger
from scripts.Base import Base


class SwProxy(Base):
    def deal_req(self):
        self.reqheader[b"user-agent"] = b"your ua!"
        return self.url, self.reqheader, self.reqbody

