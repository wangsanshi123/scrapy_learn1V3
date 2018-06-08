# -*- coding: utf-8 -*-
import re
from time import strftime, strptime

import scrapy

from scrapy_learn1v3.items import Bgr
from scrapy_learn1v3.utils.databaseUtil import MysqlUtil


class BgrSpider(scrapy.Spider):
    "由于首页的格式不一样，且内容 不是很多，所以不专门爬取"
    name = 'bgr'

    page = 2
    base_Url = "http://www.bgr.in/category/news/page/{}/"
    start_urls = [base_Url.format(page)]

    def __init__(self):
        self.mysqlUtil = MysqlUtil()
        self.mysqlUtil.cur.execute("SELECT MAX(post_time) FROM `bgr` ")
        self.mysqlUtil.conn.commit()
        self.max_post_time = str(self.mysqlUtil.cur.fetchone()["MAX(post_time)"])
        pass

    def parse(self, response):
        # print(response.text)
        divs = response.xpath(".//div[contains(@class,'widget-list news_sec')]")
        print(len(divs))
        for div in divs:
            title = div.xpath(".//h3[@class='media-heading']/a/@title").extract_first()
            content_url = div.xpath(".//h3[@class='media-heading']/a/@href").extract_first()
            author = div.xpath(".//span[@class='name']/a/@title").extract_first()
            post_time = div.xpath(".//div[@class='time-date']").xpath("string()").extract_first()
            post_time = re.sub("\s", "", post_time)
            post_time = strftime("%Y-%m-%d %H:%M", strptime(post_time, "%I:%M%p%b%d,%Y")) if post_time else ""
            print("title:", title)
            print("post_time:", post_time)
            print("author:", author)
            print("content_url:", content_url)
            #############增量更新##########################
            if self.max_post_time and self.max_post_time != "None" and str(self.max_post_time) >= post_time:
                print("=====increasing update====", post_time)
                return
            yield Bgr(title=title, post_time=post_time, author=author, content_url=content_url, isContentUpdated=0)
        pass

        # nextpage

        nextPage = response.xpath(".//span[@class='btn btn-default']")
        if nextPage:
            self.page += 1
            yield scrapy.Request(url=self.base_Url.format(self.page))
        else:
            print("==============the last page==========================", self.page)
        pass
