# -*- coding: utf-8 -*-
from time import strptime, strftime

import scrapy

from scrapy_learn1v3.items import AmazonPhoneComment
from scrapy_learn1v3.utils.databaseUtil import MysqlUtil


class AmazoncommentsSpider(scrapy.Spider):
    name = 'amazoncomments'  #用于评论的爬取
    headUrl = "https://www.amazon.in/"
    ajax_headUrl = "https://www.amazon.in/ss/customer-reviews/ajax/reviews/get/ref=cm_cr_arp_d_paging_btm_{}"

    def __init__(self):
        self.mysqlUtil = MysqlUtil()

    def start_requests(self):
        dataSet = self.mysqlUtil.select('amazon_phone_info')
        time = 0
        for item in dataSet:
            if time > 0:
                break
            time += 1
            comment_url = item['comment_url']
            comment_num = item['comment_num']

            asin = item['asin']
            print("comment_url:", comment_url)
            comment_url = "https://www.amazon.in//Vivo-Y66-Matte-Black-RAM/product-reviews/B06XR9QTGB/ref=dpx_acr_txt?showViewpoints=1"
            comment_url = comment_url.replace("sortBy=helpful", "sortBy=recent")
            yield scrapy.Request(url=comment_url, meta={'asin': asin, 'comment_num': comment_num})

            pass

        pass

    def parse(self, response):
        print("response:", response)
        print("======:", len((response.xpath(".//*[@id='cm_cr-review_list']/div").extract())))
        asin = response.meta["asin"]
        comment_num = response.meta["comment_num"]

        time = 0
        divs = response.xpath(".//*[@id='cm_cr-review_list']/div")

        for item in divs:
            time += 1
            if time == len(divs):  # 排除边界
                break
            stars = item.xpath('.//div[1]/a[1]/i/span/text()').extract_first()
            stars = 0 if not stars else stars
            author = item.xpath('.//div[2]/span[1]/a/text()').extract_first()
            date = item.xpath('.//div[2]/span[5]/text()').extract_first()
            date = item.xpath('.//div[2]/span[3]/text()').extract_first() if not date else date
            date = strftime("%Y-%m-%d", strptime(date.replace('on', '').strip(), "%d %B %Y")) if date else ""

            content = item.xpath('.//div[4]/span/text()').extract_first()
            content = "" if not content else content
            digg_count = item.xpath(
                './/div[5]/div/span[1]/span/span[3]/span/text()').extract_first()
            digg_count = digg_count.strip() if digg_count else 0
            digg_count = 1 if digg_count != 0 and digg_count.startswith('One') else digg_count

            lastCommentDate = self.mysqlUtil.select('amazon_phone_info', ['lastCommentDate'], {'asin=': asin})[0][
                'lastCommentDate']

            if lastCommentDate and str(lastCommentDate) >= date:  # 用于增量更新
                print("=====increasing update====",date)
                return

            if time == 1:  # 记录下最新评论的时间
                self.mysqlUtil.cur.execute("update amazon_phone_info set lastCommentDate=%s where asin=%s",
                                           (date, asin))
                self.mysqlUtil.conn.commit()

            # print("stars:", stars)
            # print("author:", author)
            # print("date:", date)
            # print("content:", content)
            # print("digg_count:", digg_count)
            # print("============")
            yield AmazonPhoneComment(asin=asin, score=stars, author=author, date=date, content=content,
                                     digg_num=digg_count)

        # url = response.xpath('//*[@id="cm_cr-pagination_bar"]/ul/li[6]/a/@href').extract_first()
        url = response.xpath(".//*[@id='cm_cr-pagination_bar']/ul/li[@class='a-last']/a/@href").extract_first()
        # url = response.xpath(".//*[@id='cm_cr-pagination_bar']/ul/li[9]/a/@href").extract_first() if not url else url
        print("url:", url)
        if url:
            url = self.headUrl + url
            yield scrapy.Request(url=url, meta={'asin': asin, 'comment_num': comment_num})
        else:
            print("failed:", response.url)

        pass
