# -*- coding: utf-8 -*-
import re

import scrapy

from scrapy_learn1v3.items import BgrContent
from scrapy_learn1v3.utils.databaseUtil import MysqlUtil


class BgrcontentSpider(scrapy.Spider):
    name = 'bgrcontent'
    start_urls = [
        'http://www.bgr.in/news/facebook-cambridge-analytica-scandal-what-mark-zuckerberg-said-about-the-major-breach-of-trust/']
    "http://www.bgr.in/news/facebook-cambridge-analytica-scandal-what-mark-zuckerberg-said-about-the-major-breach-of-trust/"

    def __init__(self):
        self.mysqlUtil = MysqlUtil()

    def start_requests(self):
        dataSet = self.mysqlUtil.select('bgr')
        time = 0
        for item in dataSet:
            # if time > 0:
            #     break
            # time += 1

            content_url = item["content_url"]
            title = item["title"]
            isContentUpdated = item["isContentUpdated"]
            if not isContentUpdated:  # 只有没用更新过的新闻内容才会被爬取
                yield scrapy.Request(url=content_url)
            else:
                print(title, "=================已经更新过了")
            pass

    def parse(self, response):
        title = response.xpath(".//h1[@class='title_name']/text()").extract_first()
        content = response.xpath(".//div[@class='article-content']").xpath("string()").extract_first()
        ##################去除script中的内容################################### #####
        for script in response.xpath(".//div[@class='article-content']/script"):
            content_extra = script.xpath("string()").extract_first()
            content = content.replace(content_extra, "")
            pass
        ############################################################

        # 去除文章末尾的广告部分
        content = content.split("Published Date") if content else ""
        content = content[0].replace("\n", "").strip() if content else ""
        # 去除换行，空格
        content = re.sub("[\n\r]", "", content) if content else ""

        # print("content:", content)
        print("title:", title)
        ### 更新新闻概要表的isContentUpdated字段，表示该新闻的内容已经被爬取了
        self.mysqlUtil.cur.execute("update bgr set isContentUpdated=%s where title=%s",
                                   (1, title))
        self.mysqlUtil.conn.commit()
        yield BgrContent(title=title, content=content)
        pass
