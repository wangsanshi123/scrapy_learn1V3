# -*- coding: utf-8 -*-
import hashlib
import json
import re
from time import strftime, localtime

import scrapy
from scrapy import Selector

from scrapy_learn1v3.items import TwitterDetails
from scrapy_learn1v3.utils.databaseUtil import MysqlUtil


class TwitterDetailSpider(scrapy.Spider):
    name = 'twitterdetail'

    "https://twitter.com/Vivo_India/status/926683025022291969"
    "https://twitter.com/i/Vivo_India/conversation/970594495556288512?include_available_features=1&include_entities=1&max_position=DAACDwABCgAAAAUNeJgPttQwAQ14QG4QlUAFDXhcmUSX0AANeD-drRUwAA14PrI7lEAACAADAAAAAQIABAAAAA&reset_error_state=false"

    def __init__(self):
        self.baseUrl = "https://twitter.com/{}/status/"
        self.mysqlUtil = MysqlUtil()

    def start_requests(self):
        # get id from database
        dataSet = self.mysqlUtil.select('twitter_text')
        time = 0
        for item in dataSet:
            # if time > 2:
            #     break
            # time += 1
            id = re.sub("\D*", "", item["id"])
            account_name = item["account_name"]

            url = self.baseUrl.format(account_name) + id
            # url = "https://twitter.com/Vivo_India/status/970594495556288512"
            # self.id = 970594495556288512
            isContentUpdated = item["isContentUpdated"]
            if not isContentUpdated:  # 只有没用更新过的新闻内容才会被爬取
                yield scrapy.Request(url=url,
                                     meta={"id": id, "account_name": account_name})
                pass

        pass

    def parse(self, response):
        id = response.meta["id"]
        account_name = response.meta["account_name"]

        lis = response.xpath(".//li[contains(@id,'stream-item-tweet')]")
        # print("lis:", len(lis))
        time = 0
        for li in lis:
            time += 1
            content = li.xpath(".//div[@class='js-tweet-text-container']").xpath("string(.)").extract_first()
            content = content.strip() if content else None
            post_time = li.xpath(
                ".//span[contains(@class,'_timestamp js-short-timestamp')]/@data-time").extract_first()
            post_time = strftime("%Y-%m-%d %H:%M:%S", localtime(float(post_time))) if post_time else None
            author = li.xpath(
                ".//span[@class='FullNameGroup']/strong[contains(@class,'fullname show-popup-with-id u-textTruncate')]/text()").extract_first()

            # print("content:", content)
            # print("post_time:", post_time)
            # print("author:", author)

            #####################增量更新########################################

            ### 更新twitter概要表的isContentUpdated字段，表示该twitterd的评论已经被爬取了
            self.mysqlUtil.cur.execute("update twitter_text set isContentUpdated=%s where id=%s",
                                       (1, id))
            ######################增量更新###################################

            if author and content and post_time:
                unique_posttime_author_content = author + content + post_time
                unique_posttime_author_content = hashlib.md5(unique_posttime_author_content.encode('utf-8')).hexdigest()
            else:
                continue
            if post_time and post_time.strip() and content and content.strip() and author and author.strip():
                yield TwitterDetails(id=id, post_time=post_time, content=content, author=author,unique_posttime_author_content = unique_posttime_author_content)

        min_position = response.xpath(".//div[contains(@class,'stream-container')]/@data-min-position").extract_first()
        # print("min_position:", min_position)
        if min_position:
            url = "https://twitter.com/i/{}/conversation/{}?include_available_features=1&include_entities=1&max_position={}&reset_error_state=false".format(
                account_name, id, min_position)

            yield scrapy.Request(url=url, callback=self.parseMore, meta={"id": id, "account_name": "account_name"})
        pass

    # has more replys
    def parseMore(self, response):
        id = response.meta["id"]
        account_name = response.meta["account_name"]

        data = json.loads(response.body.decode("utf-8"))
        lis = Selector(text=data['items_html']).xpath(".//li[contains(@class,'ThreadedConversation')]")
        # print("lis:", len(lis))
        # with open("temp4.html", "w") as f:
        #     f.write(json.dumps(data['items_html']))

        for li in lis:
            content = li.xpath(".//div[@class='js-tweet-text-container']").xpath("string(.)").extract_first()
            content = content.strip() if content else None
            "_timestamp js-short-timestamp"
            post_time = li.xpath(
                ".//span[contains(@class,'_timestamp js-short-timestamp')]/@data-time").extract_first()
            post_time = strftime("%Y-%m-%d %H:%M:%S", localtime(float(post_time))) if post_time else None
            author = li.xpath(
                ".//span[@class='FullNameGroup']/strong[contains(@class,'fullname show-popup-with-id u-textTruncate')]/text()").extract_first()
            # print("author:", author)

            # print("post_time:", post_time)

            if author and content and post_time:
                unique_posttime_author_content = author + content + post_time
                unique_posttime_author_content = hashlib.md5(unique_posttime_author_content.encode('utf-8')).hexdigest()
            else:
                continue
            if post_time and post_time.strip() and content and content.strip() and author and author.strip():
                yield TwitterDetails(id=id, post_time=post_time, content=content, author=author,
                                     unique_posttime_author_content=unique_posttime_author_content)

            pass

        min_position = data['min_position']
        has_more_items = data["has_more_items"]
        print("has_more_items:", has_more_items)
        if has_more_items:
            url = "https://twitter.com/i/{}/conversation/{}?include_available_features=1&include_entities=1&max_position={}&reset_error_state=false".format(
                account_name, id, min_position)

            yield scrapy.Request(url=url, callback=self.parseMore, meta={"id": id, "account_name": account_name})
            pass

        pass
