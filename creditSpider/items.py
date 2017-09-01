# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CreditspiderItem(scrapy.Item):
    """
    信用分数对象类，用户结构化爬取过来的数据
    """
    classify = scrapy.Field()  # 行业类别
    target_act = scrapy.Field()  # 指标名称
    score = scrapy.Field()  # 分数


# 违章数据item
# "jszh": "违法驾驶证号"
# "wfsj": "违法时间"
# "wfdz": "行为地点"
# "wfxw": "行为代码"
# "wfjfs": "违法计分数"
# "fkje": "罚款金额"
# "cljg": "处理机构代码"
# "jkbj": "是否交款"
# "dh": "当事人电话号码"
# "dsr": "当事人姓名"
# "hphm": "车牌号码"
# "hpzl": "号牌种类"
# "clsj": "处理时间"
# "fzjg": "车牌地区号-贵A"
# "wfnr": "违法内容"
# "yhmc": "业户名称(企业名称)"

class WeiZhangActionItem(scrapy.Item):
    """
    违章行为数据结构
    """
    jszh = scrapy.Field()
    wfsj = scrapy.Field()
    wfdz = scrapy.Field()
    wfxw = scrapy.Field()
    wfjfs = scrapy.Field()
    fkje = scrapy.Field()
    cljg = scrapy.Field()
    jkbj = scrapy.Field()
    dh = scrapy.Field()
    dsr = scrapy.Field()
    hphm = scrapy.Field()
    hpzl = scrapy.Field()
    clsj = scrapy.Field()
    fzjg = scrapy.Field()
    wfnr = scrapy.Field()
    yhmc = scrapy.Field()
