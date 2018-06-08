# -*- coding: utf-8 -*-
import re
from time import strptime, strftime

import scrapy

from scrapy_learn1v3.items import ComplaintboardComments, Complaintboard


class ComplaintboardSpider(scrapy.Spider):
    name = "complaintboard"
    baseUrl = "https://www.complaintboard.in"

    def start_requests(self):
        'vivo'
        keywords = ['xiaomi','huawei']
        for item in keywords:
            url = "https://www.complaintboard.in/?search={}".format(item)
            yield scrapy.Request(url=url, meta={"keyword": item})

    def parse(self, response):
        keyword = response.meta['keyword']

        divs = response.xpath('//*[@id="c"]')
        time = 0
        for div in divs:
            # if time > 3:
            #     break
            # time += 1

            url = div.xpath('.//tr[1]/td/h4/a/@href').extract_first()
            date = div.xpath('.//tr[2]/td/text()[2]').extract_first()
            date = strftime("%Y-%m-%d", strptime(date.strip(), "%b %d, %Y")) if date else date

            url = re.sub(r'.html|/page/\d+', '/page/1', self.baseUrl + url.split('#')[0])

            print("url:", url)
            # print("date:", date)

            yield Complaintboard(keyword=keyword, date=date, url=url)
            yield scrapy.Request(url=url, callback=self.parseDetail)

        nextPage = response.xpath(".//a[text()='Next']/@href").extract_first()

        if nextPage:
            print("nextPage:" + self.baseUrl + nextPage)
            url = self.baseUrl + nextPage
            yield scrapy.Request(url, meta={"keyword": keyword})

        pass

    def parseDetail(self, response):
        # print(response)
        divs = response.xpath('//div[starts-with(@id,"c")]')
        # time = 0
        for div in divs:
            # if time > 5:
            #     break
            # time += 1

            author = div.xpath('.//table//tr[1]/td[1]/a/text()').extract_first()
            date = div.xpath('table//tr[1]/td[2]')[1].xpath("text()").extract_first()
            date = strftime("%Y-%m-%d", strptime(date.strip(), "%b %d, %Y")) if date else date

            title = div.xpath('.//table//tr[2]/td/div/h4/text()').extract_first()
            content = div.xpath('.//table//tr[2]/td/div/div/text()').extract_first()

            # print("author:", author)
            # print("date:", date)
            # print("title:", title)
            # print("content:", content)

            yield ComplaintboardComments(author=author, date=date, title=title, content=content)

        nextPage = response.xpath(".//a[text()='Next']/@href").extract_first()
        if nextPage:
            # print("nextPage:" + self.baseUrl + nextPage)
            url = self.baseUrl + nextPage
            yield scrapy.Request(url, callback=self.parseDetail)

        pass
