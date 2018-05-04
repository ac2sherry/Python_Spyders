# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random, time
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from scrapy.http import HtmlResponse

########################################
#--------DOWNLOADER MIDDLEWARES--------#
########################################
class RandomUserAgent(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self,agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        return cls(crawler.settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        agent = random.choice(self.agents)
        request.headers.setdefault('User-Agent', agent)
        spider.logger.debug('agent: %s' % agent)
        return None

class RandomProxy(object):
    def __init__(self, iplist):  # 初始化一下数据库连接
        self.iplist = iplist

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        return cls(crawler.settings.getlist('IPLIST'))

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        proxy = random.choice(self.iplist)
        spider.logger.info('proxy: %s' % proxy)
        request.meta['proxy'] = proxy
        return None

class FixedProxy(object):
    def __init__(self, proxy):  # 初始化一下数据库连接
        self.proxy = proxy

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        return cls(crawler.settings.get('PROXY'))

    # overwrite process request
    def process_request(self, request, spider):
        # Set the location of the proxy
        request.meta['proxy'] = self.proxy
        spider.logger.debug('proxy: %s' % self.proxy)
        return None



class PhantomJSMiddleware(object):

    def __init__(self, agents, username, password):
        self.agents = agents
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome()
        # self.driver = webdriver.Chrome()
        self.driver.set_window_size(1024, 600)
        self.login()

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        # 初始化实例
        ext = cls(crawler.settings.getlist('USER_AGENTS'),
                  crawler.settings.get('USERNAME'),
                  crawler.settings.get('PASSWORD')
                  )
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    def spider_closed(self, spider):
        self.driver.quit()

    def login(self):
        # login
        agent = random.choice(self.agents)
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = agent
        # login url
        url = 'https://vk.com/login'
        driver = self.driver
        driver.get(url)
        time.sleep(1)
        # login actions
        username = driver.find_element_by_xpath('.//*[@id="email"]')
        password = driver.find_element_by_xpath('.//*[@id="pass"]')
        login_button = driver.find_element_by_xpath('//*[@id="login_button"]')
        username.send_keys(self.username)
        password.send_keys(self.password)
        login_button.click()

    def process_request(self, request, spider):
        '''return a Response object'''
        agent = random.choice(self.agents)
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = agent

        if request.meta.has_key('use_selenium'):
            if request.meta.has_key('get_photo'):
                # 需要selenium代解析的动态网页（下载照片）
                spider.logger.info('process crawl: %s' % request.url)
                spider.logger.debug('meta: %s' % request.meta)
                driver = self.driver
                driver.get(request.url)
                time.sleep(random.uniform(1,3))
                # 这里要点击一下more的按钮
                more_button = driver.find_element_by_xpath('//a[@class="pv_actions_more"]')
                more_button.click()
                time.sleep(1)
                photo_url = driver.find_element_by_xpath('//a[@id="pv_more_act_download"]')
                content = photo_url.get_attribute('href').encode('utf-8')
                return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)

            elif request.meta['use_selenium'] == True:
                # 一般动态网页 直接回传
                spider.logger.info('process crawl: %s' % request.url)
                spider.logger.debug('meta: %s' % request.meta)
                driver = self.driver
                driver.get(request.url)
                time.sleep(random.uniform(1,3))
                content = driver.page_source.encode('utf-8')
                return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)