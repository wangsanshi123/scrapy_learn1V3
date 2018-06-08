# -*- coding: utf-8 -*-
from time import strftime, strptime

import scrapy

from scrapy_learn1v3.items import Mobilescoutcomments
from scrapy_learn1v3.utils.databaseUtil import MysqlUtil


class MobilescoutcommentsSpider(scrapy.Spider):
    "由于评论数不多，暂时不做增量更新了"
    "由于最多的评论数为9，暂时不做翻页"
    name = 'mobilescoutcomments'
    baseUrl = "https://www.mobilescout.com"

    def __init__(self):
        self.mysqlUtil = MysqlUtil()

    def start_requests(self):
        dataSet = self.mysqlUtil.select('mobilescout')
        time = 0
        for item in dataSet:
            # if time > 3:
            #     break
            # time += 1
            brand = item["brand"]
            title = item["title"]
            reply = item["reply"]
            if int(reply) > 0:
                # print("reply:", reply)
                comment_url = self.baseUrl + item["comment_url"]
                print("comment_url:", comment_url)
                yield scrapy.Request(url=comment_url, meta={"brand": brand, "title": title})
        pass

    def parse(self, response):
        brand = response.meta["brand"]
        title = response.meta["title"]

        lis = response.xpath(".//li[contains(@id,'post_')]")
        print("lis:", len(lis))
        for li in lis[1:]:
            post_time = li.xpath(".//span[@class='date']").xpath("string()").extract_first()
            print("post_time_before:", post_time)
            post_time = strftime("%Y-%m-%d %H:%M", strptime(post_time, "%m-%d-%Y, %I:%M %p")) if post_time else ""

            author = li.xpath(".//a[@class='username offline popupctrl']").xpath("string()").extract_first()
            author_title = li.xpath(".//span[@class='usertitle']").xpath("string()").extract_first()
            author_title = author_title.strip() if author_title else ""
            join_time = li.xpath(".//dl[@class='userinfo_extra']/dd/text()").extract_first()
            join_time = strftime("%Y-%m-%d", strptime(join_time, "%b %Y"
                                                                 "")) if join_time else ""

            posts = li.xpath(".//dl[@class='userinfo_extra']/dd[2]/text()").extract_first()
            posts = posts.replace(",", "") if posts else ""
            # content = li.xpath(".//div[@class='postrow']").xpath("string()").extract_first()
            content = li.xpath(".//div[contains(@id,'post_message')]").xpath("string()").extract_first()
            # content = li.xpath(".//div[contains(@id,'post_message')]/blockquote/text()").extract_first()
            content_extra = li.xpath(".//div[contains(@class,'quote_container')]").xpath("string()").extract_first()
            if content_extra:
                content = content.replace(content_extra, "")
            content = content.strip() if content else ""
            print("post_time:", post_time)
            print("author:", author)

            print("author_title:", author_title)
            print("join_time:", join_time)
            print("posts:", posts)
            print("content:", content)
            # print("content_extra:", content_extra)
            print("==========================================")

            yield Mobilescoutcomments(brand=brand, title=title, post_time=post_time, author=author,
                                      author_title=author_title, join_time=join_time,
                                      posts=posts, content=content)

        pass
