# -*- coding: utf-8 -*-
import scrapy
import json

class TongjijuSpider(scrapy.Spider):
    name = "tongjiju"

    def start_requests(self):
        url = 'http://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=hgyd&rowcode=zb&colcode=sj&wds=%5B%5D&dfwds=%5B%7B%22wdcode%22%3A%22sj%22%2C%22valuecode%22%3A%22201212%22%7D%5D&k1=1513330343319'
        yield scrapy.Request(url)
    def parse(self, response):
        data = json.loads(response.text)
        # print(data['returndata']['datanodes'][0])
        # print(data['returndata']['datanodes'][1])

        print(response.text)


        pass
    