# -*- coding: utf-8 -*-
from time import strftime, strptime

import scrapy

from scrapy_learn1v3.items import MysmartpriceComments
from scrapy_learn1v3.utils.databaseUtil import MysqlUtil


class MysmartpricecommentsSpider(scrapy.Spider):
    "由于评论量不足，且只能看到10条评论，且评论不能严格按照时间排序，所以不做增量更新，每次都爬取尽可能多的评论，然后去重保存"
    name = 'mysmartpricecomments'

    def __init__(self):
        self.mysqlUtil = MysqlUtil()

    def start_requests(self):
        dataSet = self.mysqlUtil.select('mysmartprice')
        time = 0
        for item in dataSet:
            # if time > 0:
            #     break
            # time += 1
            brand = item["brand"]
            model = item["model"]
            comment_num = item["comment_num"]
            comment_url = item["comment_url"]
            if comment_num > 0:
                print("comment_url:", comment_url)
                yield scrapy.Request(url=comment_url, meta={"brand": brand, "model": model})
            pass

    def parse(self, response):
        brand = response.meta["brand"]
        model = response.meta["model"]

        divs = response.xpath(".//div[@class='review_item']")
        time = 0
        for div in divs:
            # if time > 0:
            #     break
            # time += 1
            author = div.xpath(".//div[@class='user_name']/text()").extract_first()
            post_time = div.xpath(".//div[@class='review_date']/text()").extract_first()

            post_time = strftime("%Y-%m-%d", strptime(post_time, "%B %d, %Y"
                                                                 "")) if post_time else ""

            likes = div.xpath(".//span[@class='review-useful-count']").xpath("string()").extract_first()
            topic = div.xpath(".//div[@class='review_heading']").xpath("string()").extract_first()

            content = div.xpath(".//div[@class='review_details']").xpath("string()").extract_first()
            star = div.xpath(".//div[@class='review_user_rating_bar_out']/@data-rating").extract_first()

            # print("author:", author)
            #
            print("post_time:", post_time)
            # print("likes:", likes)
            # print("topic:", topic)
            # print("content:", content)
            # print("star:", star)
            print("============================================")
            yield MysmartpriceComments(brand=brand, model=model, author=author, post_time=post_time, likes=likes,
                                       topic=topic,
                                       content=content, star=star)
            pass

        pass
