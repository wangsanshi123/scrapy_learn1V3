# -*- coding: utf-8 -*-
import json
import re
from time import localtime, strftime

import scrapy
from scrapy import Selector
from scrapy.shell import inspect_response

from scrapy_learn1v3.items import TwitterAccount, TwitterText
from scrapy_learn1v3.utils.databaseUtil import MysqlUtil


class TwitterSpider(scrapy.Spider):
    name = 'twitter'

    "https://twitter.com/Vivo_India"
    "https://twitter.com/i/profiles/show/Vivo_India/timeline/tweets?include_available_features=1&include_entities=1&max_position=878125507346288640&reset_error_state=false"
    "https://twitter.com/i/profiles/show/Vivo_India/timeline/tweets?include_available_features=1&include_entities=1&max_position=937192176059949057&reset_error_state=false"

    def __init__(self):
        self.time = 0
        self.mysqlUtil = MysqlUtil()
        self.mysqlUtil.cur.execute("SELECT MAX(post_time) FROM `twitter_text` ")
        self.mysqlUtil.conn.commit()
        self.max_post_time = str(self.mysqlUtil.cur.fetchone()["MAX(post_time)"])

    def start_requests(self):
        # accounts = ['Vivo_India','Vivoemrede', 'Huawei']
        accounts = ['Vivo_India']
        for account in accounts:
            self.account = account

            yield scrapy.Request(url='https://twitter.com/{}?lang=en'.format(account))

    def parse(self, response):
        "解析twitter账户信息"
        twitter_num = response.xpath(
            ".//li[@class='ProfileNav-item ProfileNav-item--tweets is-active']//span[@class='ProfileNav-value']/@data-count").extract_first()
        following = response.xpath(
            ".//li[@class='ProfileNav-item ProfileNav-item--following']//span[@class='ProfileNav-value']/@data-count").extract_first()
        followers = response.xpath(
            ".//li[@class='ProfileNav-item ProfileNav-item--followers']//span[@class='ProfileNav-value']/@data-count").extract_first()
        likes = response.xpath(
            ".//li[@class='ProfileNav-item ProfileNav-item--favorites']//span[@class='ProfileNav-value']/@data-count").extract_first()
        place = response.xpath(".//span[@class='ProfileHeaderCard-locationText u-dir']").xpath(
            "string(.)").extract_first().strip()
        min_position = response.xpath(".//div[contains(@class,'stream-container')]/@data-min-position").extract_first()

        # print('twitter_num:', twitter_num)
        # print('following:', following)
        #
        # print('followers:', followers)
        # print('likes:', likes)
        #
        # print('place:', place)

        yield TwitterAccount(acount_name=self.account, twitter_num=twitter_num, following=following,
                             followers=followers, likes=likes, place=place)

        # print('min_position:', min_position)
        url = "https://twitter.com/i/profiles/show/{}/timeline/tweets?include_available_features=1&include_entities=1&max_position={}&reset_error_state=false".format(
            self.account, min_position)
        yield scrapy.Request(url, callback=self.parse_page)

    pass

    def parse_page(self, response):
        "解析twitter文章相关信息"
        data = json.loads(response.body.decode("utf-8"))
        lis = Selector(text=data['items_html']).xpath(".//li[contains(@id,'stream-item-tweet')]")

        time = 0
        # print("lis:", len(lis))

        for li in lis:
            # if time > 0:
            #     break
            # time += 1
            reply = li.xpath(".//span[@class='ProfileTweet-action--reply u-hiddenVisually']").xpath(
                "string(.)").extract_first()

            retweet = li.xpath(".//span[@class='ProfileTweet-action--retweet u-hiddenVisually']").xpath(
                "string(.)").extract_first()
            likes = li.xpath(".//span[@class='ProfileTweet-action--favorite u-hiddenVisually']").xpath(
                "string(.)").extract_first()

            id = li.xpath("./@id").extract_first()
            post_time = li.xpath(".//span[contains(@class,'_timestamp js-short-timestamp')]/@data-time").extract_first()
            content = li.xpath(".//div[@class='js-tweet-text-container']").xpath("string(.)").extract_first()
            content = content.strip() if content else None

            reply = self.dropSuffix(reply)
            retweet = self.dropSuffix(retweet)
            likes = self.dropSuffix(likes)
            post_time = strftime("%Y-%m-%d %H:%M:%S", localtime(float(post_time))) if post_time else ""

            # print("id:", id)
            # print("content:", content)
            # print("post_time:", post_time)
            #############增量更新##########################
            if self.max_post_time and self.max_post_time != "None" and str(self.max_post_time) >= post_time:
                print("=====increasing update====", post_time)
                return
            if reply and reply.strip() and retweet and retweet.strip() and likes and likes.strip() and content and content.strip() and post_time and post_time.strip():
                yield TwitterText(acount_name=self.account, reply=reply, retweet=retweet, likes=likes, id=id,
                                  content=content, post_time=post_time, isContentUpdated=0)

            pass
        min_position = data['min_position']
        url = "https://twitter.com/i/profiles/show/{}/timeline/tweets?include_available_features=1&include_entities=1&max_position={}&reset_error_state=false".format(
            self.account, min_position)

        # get next page
        has_more_items = data["has_more_items"]
        if has_more_items:
            yield scrapy.Request(url=url, callback=self.parse_page, meta={'account': self.account})
        else:
            print("=======over======")
            print("has_more_items", has_more_items)
            print("url:", url)
            print("post_time:", post_time)
        pass

    def dropSuffix(self, item):
        '''去掉评论，转发，喜欢后面的单词，eg：25 likes--> 25'''
        if item:
            temp = item.strip().split(" ")[0]
            return re.sub("\D", '', temp)
        else:
            return 0
        pass
