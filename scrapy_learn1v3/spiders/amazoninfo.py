# -*- coding: utf-8 -*-
import scrapy

from scrapy_learn1v3.utils.amazonutils import getBrandModel


class AmazoninfoSpider(scrapy.Spider):
    name = 'amazoninfo'

    # "https://www.amazon.in/s/ref=nb_sb_noss_2?url=node%3D1805560031&field-keywords=vivo+Y55&rh=n%3A976419031%2Cn%3A1389401031%2Cn%3A1389432031%2Cn%3A1805560031%2Ck%3Avivo+Y55"
    def start_requests(self):
        time = 0
        for brand, model in getBrandModel():
            if time > 0:
                break
            time += 1

            keyword = brand + "+" + model
            url = self.baseUrl.format(keyword, keyword)
            yield scrapy.Request(url=url, meta={'brand': brand, 'model': model})

        pass

    def parse(self, response):


        pass
