# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging

import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


#   action_info_id  ---表主键【自动生成】
#   ep_id           ---从yhmc查找id【填充】
#   action_type     ---违章行为类型 【固定】
#   case_reason     ---违章案由 通过wfxw查找我们的映射表【填充】
#   vehicle_number  ---车牌号码 hphm 【填充】
#   action_time     ---行为时间 wfsj 【填充】
#   action_place    ---行为地点 wfdz 【填充】
#   end_case_status ---结案状态？怎样算结案状态？【填充】
#   process_org     ---处理机构 【填充】
#   action_reason   ---行为内容 wfnr 【填充】
#   action_source   ---行为来源 3 【填充】 来自交换
#   action_integration ---行为分值，【填充】先通过wfxw查找我们的映射表，然后取得分数
#   action_status      ---行为状态，【填充】正常 1

# 清洗管道
class CleanResponseData(object):
    def process_item(self, item, spider):
        return item


class StoreResponseData(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.insertWeizhang = """insert into company_behavior(ep_id, action_type, case_reason, vehicle_number,
                                    action_time,action_place,end_case_status,process_org,action_reason,action_source,
                                    action_integration,action_status)
                                  values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    # pipeline默认调用
    def process_item(self, item, spider):
        """
        处理数据的持久化，通常要把数据转入到数据库
        :param item:
        :param spider:
        :return:
        """
        self.dbpool.runInteraction(self._do_insert, dict(item), spider)

    # 将每行更新或写入数据库中
    def _do_insert(self, conn, item, spider):
        conn.execute(self.insertWeizhang,
                     ('1044', 1, item['wfxw'], item['hphm'], item['wfsj'], item['wfdz'], 1, item['cljg'],
                      item['wfnr'], 3, 0, 1))

    # 异常处理
    def _handle_error(self, failue, item, spider):
        logging.info(failue)
