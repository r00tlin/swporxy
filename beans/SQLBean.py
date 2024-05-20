# !/usr/bin/env python3.7
# coding=utf-8
# Date: 2024/5/16
# Description: 
"""
基础sql类
"""

from beans import *
import threading
from lib.Log import logger


class SQLBean:
    def __init__(self):
        self.table = Base
        sql = Session()
        self.lock = threading.Lock()
        self.dbsession, self.tables = sql.session, sql.tables

    def insert(self, yourobject):
        # 插入单条数据
        try:
            result = self.dbsession.add(yourobject)
            self.lock.acquire()
            self.dbsession.commit()
            self.dbsession.flush()
            self.lock.release()
            return result
        except Exception as e:
            if self.lock.locked():
                self.lock.release()
            logger.error(f"插入数据错误: {yourobject}，详情: {e}")

    def insert_many(self, yourobjects):
        # 插入多条数据
        try:
            self.lock.acquire()
            result = self.dbsession.bulk_save_objects(yourobjects)
            self.dbsession.commit()
            self.dbsession.flush()
            self.lock.release()
            return result
        except Exception as e:
            if self.lock.locked():
                self.lock.release()
            logger.error(f"插入数据错误: {yourobjects}，详情: {e}")

    def update(self, update_dict: dict, *key):
        # 更新数据，仅支持指定主键的内容更新
        # 能够自动识别主键，但是需要key的数量等于(大于)主键个数
        try:
            self.lock.acquire()
            if not update_dict.get("update_time"): update_dict["update_time"] = datetime.now()
            columns = self.table.__table__.primary_key.columns
            query_str = {_[0]: _[1] for _ in zip([column.name for column in columns], key)}
            result = self.dbsession.query(self.table).filter_by(**query_str).update(update_dict)
            self.dbsession.commit()
            self.dbsession.flush()
            self.lock.release()
            return result
        except Exception as e:
            if self.lock.locked():
                self.lock.release()
            logger.error(f"更新数据错误: {update_dict}，详情: {e}")

    def delete(self, **kwargs):
        # 删除数据
        result = self.dbsession.query(self.table).filter_by(**kwargs).delete()
        self.dbsession.commit()
        self.dbsession.flush()
        return result

    def select(self, query_dict: dict, offset=0, limit=10):
        # 查询数据
        result = self.dbsession.query(self.table).filter_by(**query_dict)
        return result.offset(offset).limit(limit).all(), result.count()

    def getraw(self):
        # 返回原始的dbsession，用于排序、分组等操作
        return self.dbsession.query(self.table)

    def count(self):
        # 返回数据库行数
        return self.table
