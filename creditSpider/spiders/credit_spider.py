# -*- coding: utf-8 -*-
"""
爬虫：爬取内部政务系统的数据
"""
import json
import sys  # Encoding

from faker import Factory
from scrapy import Request, FormRequest
from scrapy.spiders.init import InitSpider

from creditSpider.items import CreditspiderItem, WeiZhangActionItem

f = Factory.create()

__author__ = "chenhuang.zengch"

# Fix UTF-8 problems inside dict()
reload(sys)
sys.setdefaultencoding('utf8')


################################################################################
# Spider Class
################################################################################
class CreditSpider(InitSpider):
    name = 'creditSpider'
    handle_httpstatus_list = [400, 302]
    login_page = 'http://120.24.161.191/Login'
    start_urls = ['http://120.24.161.191/Vio/lst']
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json"
    }

    def __init__(self):
        self.page_count = 1
        self.have_next_record = True

    def init_request(self):
        """初始化方法，第一个请求，通常是登录界面"""
        return Request(url=self.login_page, callback=self.login)

    def login(self, response):
        """生成一个登录请求，通常是把用户名和密码通过post方式进行提交"""
        return FormRequest(url='http://120.24.161.191/Login/chkLogin',
                           formdata={'username': 'gzsygj', 'password': 'ysj520'},
                           method='POST',
                           meta={'cookiejar': '1'},
                           callback=self.after_login_response)

    def after_login_response(self, response):
        """
        解析交警网站的回来的数据
        :param response:
        :return:
        """
        if "success" in response.body:
            self.log("登录成功,开始爬取数据!")

            # 生成爬取请求
            fr = FormRequest(url='http://120.24.161.191/Vio/lst',
                                 formdata={"page": str(self.page_count), "pagesize": "20"},
                                 meta={'cookiejar': response.meta["cookiejar"]},
                                 callback=self.parse_police_data)
            return fr
        else:
            self.log("登录出错!")

    # 解析交警数据
    def parse_police_data(self, response):
        """
        解析逻辑数据，
        :param response:
        :return:
        """
        html = None
        try:
            html = json.loads(response.body)
        except ValueError, e:
            return
        item = WeiZhangActionItem()
        results = html.get('Rows')
        if results:
            for r in results:
                item['jszh'] = r.get('jszh')
                item['wfsj'] = r.get('wfsj')
                item['wfdz'] = r.get('wfdz')
                item['wfxw'] = r.get('wfxw')
                item['wfjfs'] = r.get('wfjfs')
                item['fkje'] = r.get('fkje')
                item['cljg'] = r.get('cljg')
                item['jkbj'] = r.get('jkbj')
                item['dh'] = r.get('dh')
                item['dsr'] = r.get('dsr')
                item['hphm'] = r.get('hphm')
                item['hpzl'] = r.get('hpzl')
                item['clsj'] = r.get('clsj')
                item['fzjg'] = r.get('fzjg')
                item['wfnr'] = r.get('wfnr')
                item['yhmc'] = r.get('yhmc')
                yield item
                self.page_count += 1
                fr = FormRequest(url='http://120.24.161.191/Vio/lst',
                                 formdata={"page": str(self.page_count), "pagesize": "20"},
                                 meta={'cookiejar': response.meta["cookiejar"],'dont_redirect': True},
                                 callback=self.parse_police_data)
                yield fr




