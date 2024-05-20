# !/usr/bin/env python3.7
# coding=utf-8

from scripts.Base import Base
from beans.SWProxyBean import SWProxy_Record


class SwProxy(Base):
    def deal_store(self):
        if 'headers'.encode("utf-8") in self.rspbody:
            return SWProxy_Record(**self.standard())
