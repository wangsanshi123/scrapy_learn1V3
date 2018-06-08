# -*- coding: utf-8 -*-
import re

import scrapy

from scrapy_learn1v3.items import MobileMi
from scrapy_learn1v3.utils.databaseUtil import MysqlUtil


class MobilemiSpider(scrapy.Spider):
    "评分和评论数等参数无法直接获得"
    name = 'mobilemi'
    "http://mobile.mi.com/in/"
    'http://mobile.mi.com/in/mix2/?RNType=product&product_id=mix2'
    'http://mobile.mi.com/in/redmi-y1/?RNType=product&product_id=redmi-y1'
    start_urls = ['http://mobile.mi.com/in/redmi-5/?RNType=product&product_id=redmi-5%0A#specs']

    def start_requests(self):
        with open("mobilemi.txt", 'r')as f:
            for line in f.readlines():
                infos = line.split(",")
                brand = infos[0]
                model = infos[1]
                url = infos[2]
                yield scrapy.Request(url=url + "#specs", meta={"brand": brand, "model": model, "url": url})
        pass

    def parse(self, response):

        brand = response.meta["brand"]
        model = response.meta["model"]
        comment_url = response.meta["url"].replace("#specs", "#review")

        configure = response.xpath(".//*[contains(@class,'main-con overview-con')]").xpath(
            "string()").extract_first()
        configure = response.xpath(".//*[@class='main-con specs-con']").xpath(
            "string()").extract_first() if not configure else configure

        try:
            configure = re.split("\s", configure) if configure else ""
        except:
            print("....")
            pass

        if configure and len(configure) > 1:
            print("configure:", len(configure))
            configure = configure[1:len(configure)]
            configure = [item.strip() for item in configure if item]
            configure = " ".join(configure)
            # print("configures:", " ".join(configure))
            print("===============================")
            lastCommentdate = self.findMaxPostTime("mobilemi", brand, model)
            match = re.search(r'product_id=(.*)', comment_url)
            if match:
                product_id = match.groups()[0]
            else:
                product_id = ""
            yield MobileMi(brand=brand, model=model, product_id=product_id, configure=configure,
                           comment_url=comment_url,
                           lastCommentdate=lastCommentdate)

        pass

    def findMaxPostTime(self, table, brand, model):
        "找到指定表和字段的最大post_time"
        mysqlUtil = MysqlUtil()
        mysqlUtil.cur.execute("SELECT MAX(lastCommentdate) FROM {} WHERE brand=%s and model=%s".format(table),
                              (brand, model))
        mysqlUtil.conn.commit()
        max_post_time = str(mysqlUtil.cur.fetchone()["MAX(lastCommentdate)"])
        return max_post_time
        pass
