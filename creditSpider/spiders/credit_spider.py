# -*- coding: utf-8 -*-
"""

"""

import sys  # Encoding
import os  # file path checks
import logging  # logger
import json  # json extract

from scrapy.http import Request, FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.spiders.init import InitSpider

from creditSpider.items import CreditspiderItem

__author__ = "chenhuang.zengch"

# Fix UTF-8 problems inside dict()
reload(sys)
sys.setdefaultencoding('utf8')


################################################################################
# Spider Class
################################################################################
class CreditSpider(InitSpider):
    """
    Crawlpy Class
    """

    ########################################
    # Scrapy Variables
    ########################################
    name = "creditSpider"

    # Link extraction rules
    # To be initialized
    rules = ()

    # Store all urls in order to
    # filter duplicates
    duplicates = []

    # scrapy domain/url vars
    # To be initialized
    allowed_domains = []
    start_urls = []

    ########################################
    # Configuration
    ########################################

    # Main JSON Configuration dict
    config = None
    config_defaults = dict({
        'proto': 'http',
        'domain': 'localhost',
        'depth': 3,
        'ignores': [],
        'httpstatus_list': [],
        'login': {
            'enabled': False,
            'method': 'post',
            'action': '/login.php',
            'failure': 'Password is incorrect',
            'fields': {
                'username': 'john',
                'password': 'doe'
            },
            'csrf': {
                'enabled': False,
                'field': 'csrf'
            }
        },
        "spiderPage": {
            "requestUrl": "/Vio/list",
            "method": "POST",
            "requestParam": {
                "page": "1",
                "pageSize": "20"
            }
        },
        'store': {
            'enabled': False,
            'path': './data'
        }
    })

    ########################################
    # Helper variables
    ########################################

    base_url = ''  # (http|https)://domain.tld
    login_url = ''  # (http|https)://domain.tld/path/to/login

    # Abort flag
    abort = False

    ########################################
    # Methods
    ########################################

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Constructor: overwrite parent __init__ function"""

        # Call parent init
        super(CreditSpider, self).__init__(*args, **kwargs)

        # Get command line arg provided configuration param
        config_file = kwargs.get('config')

        # Validate configuration file parameter
        if not config_file:
            logging.error('Missing argument "-a config"')
            logging.error('Usage: scrapy crawl creditSpider -a config=/path/to/config.json')
            self.abort = True

        # Check if it is actually a file
        elif not os.path.isfile(config_file):
            logging.error('Specified config file does not exist')
            logging.error('Not found in: "' + config_file + '"')
            self.abort = True

        # All good, read config
        else:
            # Load json config
            fpointer = open(config_file)
            data = fpointer.read()
            fpointer.close()

            # convert JSON to dict
            config = json.loads(data)

            # fill in default values for missing values
            self.config = dict()
            self.config['proto'] = str(config.get('proto', self.config_defaults['proto']))
            self.config['domain'] = str(config.get('domain', self.config_defaults['domain']))
            self.config['depth'] = int(config.get('depth', self.config_defaults['depth']))
            self.config['ignores'] = config.get('ignores', self.config_defaults['ignores'])
            self.config['httpstatus_list'] = config.get('httpstatus_list', self.config_defaults['httpstatus_list'])

            self.config['login'] = dict()
            self.config['login']['enabled'] = bool(
                config.get('login', dict()).get('enabled', self.config_defaults['login']['enabled']))
            self.config['login']['method'] = str(
                config.get('login', dict()).get('method', self.config_defaults['login']['method']))
            self.config['login']['action'] = str(
                config.get('login', dict()).get('action', self.config_defaults['login']['enabled']))
            self.config['login']['failure'] = str(
                config.get('login', dict()).get('failure', self.config_defaults['login']['failure']))
            self.config['login']['fields'] = config.get('login', dict()).get('fields',
                                                                             self.config_defaults['login']['fields'])
            self.config['login']['csrf'] = dict()
            self.config['login']['csrf']['enabled'] = bool(
                config.get('login', dict()).get('csrf', dict()).get('enabled',
                                                                    self.config_defaults['login']['csrf']['enabled']))
            self.config['login']['csrf']['field'] = str(config.get('login', dict()).get('csrf', dict()).get('field',
                                                                                                            self.config_defaults[
                                                                                                                'login'][
                                                                                                                'csrf'][
                                                                                                                'field']))
            self.config['store'] = dict()
            self.config['store']['enabled'] = bool(
                config.get('store', dict()).get('enabled', self.config_defaults['store']['enabled']))
            self.config['store']['path'] = str(
                config.get('store', dict()).get('path', self.config_defaults['store']['path']))

            self.config['spiderPage'] = dict()
            self.config['spiderPage']['requestUrl'] = str(
                config.get('spiderPage', dict()).get('requestUrl', self.config_defaults['spiderPage']['requestUrl']))
            self.config['spiderPage']['method'] = str(
                config.get('spiderPage', dict()).get('method', self.config_defaults['spiderPage']['method']))

            self.config['spiderPage']['requestParam'] = dict()
            self.config['spiderPage']['requestParam']['page'] = str(config.get('spiderPage', dict()).
                                                                    get('requestParam', dict()).get('page',
                                                                                                    self.config_defaults[
                                                                                                        'spiderPage'][
                                                                                                        'requestParam'][
                                                                                                        'page']))

            self.config['spiderPage']['requestParam']['pageSize'] = str(config.get('spiderPage', dict()).
                                                                        get('requestParam', dict()).get('page',
                                                                                                        self.config_defaults[
                                                                                                            'spiderPage'][
                                                                                                            'requestParam'][
                                                                                                            'pageSize']))
            logging.info('Merged configuration:')
            logging.info(self.config)

            # Set scrapy globals
            self.allowed_domains = [self.config['domain']]
            self.start_urls = [self.config['proto'] + '://' + self.config['domain'] + '/Vio/lst']
            self.rules = (
                Rule(
                    LinkExtractor(
                        allow_domains=(self.allowed_domains),
                        unique=True,
                        deny=tuple(self.config['ignores']),
                    ),
                    callback='parse',
                    follow=True
                ),
            )

            # Handle more status codes
            self.handle_httpstatus_list = self.config['httpstatus_list']

            # Overwrite built-in crawling depth via own config file
            # Make sure to add +1 if we do a login (which counts as 1 level)
            # The variable will be handle by a custom middleware: MyDepthMiddleware
            # and parse it to the normal middleware: DepthMiddleware
            if self.config['login']['enabled'] and self.config['depth'] != 0:
                self.max_depth = self.config['depth'] + 1
            else:
                self.max_depth = self.config['depth']

            # Set misc globals
            self.base_url = self.config['proto'] + '://' + self.config['domain']
            self.login_url = self.config['proto'] + '://' + self.config['domain'] + \
                             self.config['login']['action']

    # ----------------------------------------------------------------------
    def init_request(self):
        """This function is called before crawling starts."""

        # Do not start a request on error,
        # simply return nothing and quit scrapy
        if self.abort:
            return

        logging.info('All set, start crawling with depth: ' + str(self.max_depth))

        # Do a login
        if self.config['login']['enabled']:
            # Start with login first
            logging.info('Login required')
            return Request(url=self.login_url, callback=self.login)
        else:
            # Start with pase function
            logging.info('Not login required')
            return Request(url=self.base_url, callback=self.parse)

    # ----------------------------------------------------------------------
    def login(self, response):
        """Generate a login request."""

        # Add CSRF data to login.
        # Note: scrapy already does this automatically, if it finds
        # pre-filled input fields. If everything works without having
        # to use this custom csrf feature, it could be removed in the future.
        if self.config['login']['csrf']['enabled']:
            field = self.config['login']['csrf']['field']
            csrf = response.xpath('//input[@name="' + field + '"]/@value')[0].extract()
            self.config['login']['fields'][field] = csrf
            logging.info('Adding CSRF data to login. Field: "' + field + '" | value: "' + csrf + "'")

        return FormRequest.from_response(
            response,
            formdata=self.config['login']['fields'],
            method=self.config['login']['method'],
            dont_filter=True,
            callback=self.post_login
        )

    # ----------------------------------------------------------------------
    def post_login(self, response):
        """
        Check the response returned by a login request to see if we are
        successfully logged in.
        """

        if self.config['login']['failure'] not in response.body:
            # Now the crawling can begin..
            logging.info('Login successful')
            return FormRequest(
                url=self.config['proto'] + '://' + self.config['domain'] + '/Vio/lst',
                formdata=self.config['spiderPage']['requestParam'],
                callback=self.parse_logic_data,
                dont_filter=True,
                method='POST')
        else:
            # Something went wrong, we couldn't log in, so nothing happens.
            logging.error('Unable to login')

            # ----------------------------------------------------------------------

    def parse(self, response):

        """
        Scrapy parse callback
        """

        # Yield current url item
        item = CreditspiderItem()
        item['title'] = response.url
        item['content'] = response.body
        logging.info("=====>")
        logging.info(item['title'])
        yield item

    def parse_logic_data(self, response):
        """
        处理爬虫爬回来的业务数据
        """
        logging.info("====>process logic data")
        logging.info("=====>url"+response.url)
        logging.info(response.body)



