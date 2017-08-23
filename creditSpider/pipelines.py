# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging


class CreditspiderPipeline(object):
    def process_item(self, item, spider):
        logging.info("==========>")
        logging.info(item['content'])
        logging.info("***********")
