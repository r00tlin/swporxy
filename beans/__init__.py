# !/usr/bin/env python3.7
# coding=utf-8
# Date: 2024/5/16
# Description: 
"""

"""
from datetime import datetime
from lib.DbConn import BaseConn, Base, Base_table
from sqlalchemy import Column, INT, INTEGER, TEXT, Text, FLOAT, String, CHAR, BOOLEAN, ForeignKey, JSON


class Session:
    """
    创建数据库连接session
    理论上只需要创建一个即可，但是随时不同的表的导入，需要持续更新(create_all操作)
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'session'):
            self.b = BaseConn()
        Base.metadata.create_all(self.b.engine)
        self.session = self.b.session
        self.tables = Base.metadata.tables.keys()

