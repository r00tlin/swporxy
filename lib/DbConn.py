# !/usr/bin/env python3.7
# coding=utf-8
# Date: 2024/5/16
# Description: 
"""
数据库连接类
"""
import os.path

from lib.Conf import config
from sqlalchemy import Column, DATETIME
from lib.Projpath import rootpath
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()


class BaseConn:
    dbc: str = config.globalvar.get("mysqldbc")
    if dbc.startswith("sqlite"):
        dbc = dbc.replace("{rootpath}", rootpath)

    # 如果不存在则创建数据库
    else:
        engine = create_engine(dbc.replace(dbc[dbc.rfind("/"):], "/mysql"))
        create_database_query = f"CREATE DATABASE IF NOT EXISTS {dbc.split('/')[-1].split('?')[0]}"
        engine.execute(create_database_query)
        # 关闭引擎连接
        engine.dispose()

    # 重新创建引擎
    engine = create_engine(dbc)

    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    # 创建session对象:
    session = DBSession()


class Base_table:
    """
    定义一些表基础操作，包括数据输出格式等
    """
    __tablename__ = ""

    # 定义两个时间属性
    create_time = Column(DATETIME, comment='创建时间')
    update_time = Column(DATETIME, comment='修改时间')

    # 定义DDL语句，将name和age列放到表的最后，都超过10000列表就不推荐了!
    create_time._creation_order = 9999
    update_time._creation_order = 10000

    def getdata(self) -> vars:
        result = vars(self)
        return {k: v for k, v in result.items() if k != "_sa_instance_state"}

    def __repr__(self):
        return str(self.getdata())
