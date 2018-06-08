# -*- coding: utf-8 -*-
import hashlib
import re
from time import strftime, strptime

import scrapy
from scrapy import Selector

from scrapy_learn1v3.items import AmazonPhoneComment
from scrapy_learn1v3.utils.databaseUtil import MysqlUtil


class AmazoncommentsNewSpider(scrapy.Spider):
    '''之前的amazon评论叶采用的是浏览器模式，此版本是直接分析网站结构的新模式'''
    name = 'amazoncomments_new'
    formdata = {'asin': "", 'deviceType': "desktop", "filterByKeyword": "",
                "filterByStar": "", "formatType": "", "pageNumber": "1", "pageSize": "10",
                "reftag": "cm_cr_getr_d_paging_btm_1", 'reviewerType': "",
                "scope": "reviewsAjax1", "shouldAppend": "undefined", "sortBy": "recent"}

    def __init__(self):
        "https://www.amazon.in//Vivo-Y66-Matte-Black-RAM/product-reviews/B06XR9QTGB/ref=dpx_acr_txt?showViewpoints=1"
        self.mysqlUtil = MysqlUtil()
        self.startUrl = "https://www.amazon.in/ss/customer-reviews/ajax/reviews/get/ref=cm_cr_getr_d_paging_btm_1"
        self.headers = {"X-Requested-With": "XMLHttpRequest",
                        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}
        # self.page = 1
        # self.pageNumber = 1
        # self.asin = ''

    def start_requests(self):
        dataSet = self.mysqlUtil.select('amazon_phone_info')
        time = 0
        for item in dataSet:
            if time > 5:
                break
            time += 1

            asin = item['asin']
            brand = item['brand']
            model = item['model']
            # asin = "B01N9J9N6A"
            print("time:", time)
            print("asin:", asin)

            self.formdata['asin'] = asin
            isContentUpdated = item["isContentUpdated"]
            if not isContentUpdated:  # 只有没用更新过的内容才会被爬取
                yield scrapy.FormRequest(self.startUrl, headers=self.headers,
                                         formdata=self.formdata,
                                         meta={"brand": brand, "model": model, "asin": asin})

        pass

    def parse(self, response):
        brand = response.meta["brand"]
        model = response.meta["model"]
        try:
            pageNumber = response.meta["pageNumber"]
        except:
            pageNumber = 1
            pass
        pageNumber += 1
        print("pageNumber:", pageNumber)

        asin = response.meta["asin"]

        divs = self.formatResponse(response)

        print("divs:", len(divs))
        time = 0
        for div in divs:
            time += 1
            temp = Selector(text=div.replace("\\", ""))
            content = temp.xpath(".//span[contains(@class,'a-size-base review-text')]/text()").extract_first()

            post_time = temp.xpath(
                ".//span[contains(@class,'a-size-base a-color-secondary review-date')]/text()").extract_first()
            post_time = strftime("%Y-%m-%d",
                                 strptime(post_time.replace('on', '').strip(), "%d %B %Y")) if post_time else ""

            author = temp.xpath(
                ".//a[contains(@class,'a-size-base a-link-normal author')]/text()").extract_first()
            content = content.strip() if content else content

            stars = temp.xpath(".//span[contains(@class,'a-icon-alt')]/text()").extract_first()
            if asin and author and content:
                unique_asin_author_content = asin + author + content
                unique_asin_author_content = hashlib.md5(unique_asin_author_content.encode('utf - 8')).hexdigest()
            else:
                continue
            # print('content:', content)
            # print('post_time:', post_time)
            # print('author:', author)
            # print('stars:', stars)

            #####################增量更新########################################
            ### 更新新闻概要表的isContentUpdated字段，表示该新闻的内容已经被爬取了
            self.mysqlUtil.cur.execute("update amazon_phone_info set isContentUpdated=%s where asin=%s",
                                       (1, asin))

            ######################增量更新###################################

            if content and post_time and author and content.strip() and post_time.strip() and author.strip():
                yield AmazonPhoneComment(brand=brand, model=model, asin=asin, score=stars, author=author,
                                         date=post_time, content=content,
                                         unique_asin_author_content=unique_asin_author_content,
                                         digg_num=0)

                pass
        pass
        # get nextpage
        if len(divs) >= 10:
            nextPage = "https://www.amazon.in/ss/customer-reviews/ajax/reviews/get/ref=cm_cr_getr_d_paging_btm_next_{}".format(
                pageNumber)
            self.formdata["pageNumber"] = str(pageNumber)
            self.formdata["reftag"] = "cm_cr_getr_d_paging_btm_{}".format(pageNumber)
            self.formdata['asin'] = asin
            yield scrapy.FormRequest(nextPage, headers=self.headers, formdata=self.formdata,
                                     meta={"pageNumber": pageNumber, "asin": asin, 'brand': brand, "model": model})
        else:
            print("url:", response.url)
        pass

    def formatResponse(self, response):
        items = response.text.split("&&&")
        divs = []
        for item in items:

            item_list = re.findall(r'"(.+?)"[,\]]', item)

            if len(item_list) >= 3 and item_list[1] == "#cm_cr-review_list":
                divs.append(item_list[2])
        pass

        return divs
