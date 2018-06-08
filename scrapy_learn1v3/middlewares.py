# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import random

import time
from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from scrapy_learn1v3.utils.amazonutils import saveUrlIgnore

logger = logging.getLogger(__name__)


class ScrapyLearn1V3SpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgent(object):
    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))  # 返回的是本类的实例cls ==RandomUserAgent

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.agents))


pass


class PhantomJSMiddleware(object):
    def process_request(self, request, spider):
        if spider.name in ["amazoncomments", "amazoncomments2"]:
            print("PhantomJS is starting...")

            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = (
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0"
            )
            # logger.info("===PhantomJS is starting...")
            driver = webdriver.PhantomJS()
            driver.get(request.url)
            try:
                ele = EC.presence_of_element_located(
                    (By.XPATH, ".//*[@id='cm_cr-pagination_bar']/ul/li[@class='a-last']/a"))
                WebDriverWait(driver, 60).until(ele)

            except:
                url = request.url
                asin = request.meta["asin"]
                comment_num = request.meta["comment_num"]

                logger.error("failed：" + url)
                page = int(url.split("=")[1])

                if page < comment_num / 10:  # 如果超时且页数不对的话就保存信息，用于重爬
                    saveUrlIgnore(request.url, asin=asin, comment_num=comment_num)
                pass

            body = driver.page_source
            # driver.close()
            return HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)
        elif spider.name is "amazon":
            print("PhantomJS is starting...")

            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = (
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0"
            )
            logger.info("===PhantomJS is starting...")
            driver = webdriver.PhantomJS()
            driver.get(request.url)
            # time.sleep(5)  # 等待5秒钟或者等底部页面加载出来，如下

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, ".//*[@id='acrPopover']")))
            except Exception as e:
                print(e)
                pass

            body = driver.page_source

            return HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)
            pass
