# -*- coding: utf-8 -*-
from time import strptime, strftime

import scrapy
from scrapy import Selector

from scrapy_learn1v3.items import Bhonko
from scrapy_learn1v3.utils.databaseUtil import MysqlUtil


class BhonkoSpider(scrapy.Spider):
    name = 'bhonko'
    page = 0
    formatdata = {"group_no": str(page)}
    url = "http://www.bhonko.in/index-post.php"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest"}

    def __init__(self):
        self.mysqlUtil = MysqlUtil()
        self.mysqlUtil.cur.execute("SELECT MAX(post_time) FROM `bhonko` ")
        self.mysqlUtil.conn.commit()
        self.max_post_time = str(self.mysqlUtil.cur.fetchone()["MAX(post_time)"])
        pass

    def start_requests(self):
        yield scrapy.FormRequest(url=self.url, headers=self.headers, formdata=self.formatdata)
        pass

    def parse(self, response):
        temp = Selector(text=response.text)
        divs = temp.xpath(".//div[contains(@class,'col-md-12 no-padd-xs')]")
        if not divs:
            # no more content
            print("==================last page=======================:", self.page)
            return
        print(len(divs))
        for item in divs:
            author = item.xpath(".//span[contains(@class,'user-name')]/text()").extract_first()
            post_time = item.xpath(".//span[contains(@class,'post-time')]/text()").extract_first()
            seller = item.xpath(
                ".//div[contains(@class,'col-md-9 col-sm-9 col-xs-9 no-padd')]/h2/text()").extract_first()

            post_time = post_time.replace("Posted on", "").strip() if post_time else ""
            print("post_time_before:", post_time)
            "21 March 2018 12:40 PM"
            post_time = strftime("%Y-%m-%d %H:%M", strptime(post_time, "%d %B %Y %I:%M %p"
                                                                       "")) if post_time else ""

            problem = item.xpath(".//div/h3/text()").extract_first()
            detail = item.xpath(".//p[contains(@class,'more')]/text()").extract_first()

            # print("author:", author)
            print("post_time:", post_time)
            # print("seller:", seller)
            # print("detail:", detail)
            print("problem:", problem)
            print("=============")
            #############增量更新##########################
            if self.max_post_time and self.max_post_time != "None" and str(self.max_post_time) >= post_time:
                print("=====increasing update====", post_time)
                return
            yield Bhonko(author=author, post_time=post_time, seller=seller, problem=problem, detail=detail)
        # nextpage
        self.page += 1
        self.formatdata["group_no"] = str(self.page)
        yield scrapy.FormRequest(url=self.url, headers=self.headers, formdata=self.formatdata)

        pass
