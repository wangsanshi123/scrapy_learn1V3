# -*- coding: utf-8 -*-
import re

import scrapy

from scrapy_learn1v3.items import GDP


class GdpSpider(scrapy.Spider):
    name = "gdp"
    start_urls = ['http://www.360doc.com/content/16/0123/11/27398134_529985505.shtml']

    def parse(self, response):
        spans = response.xpath("/html/body/div[4]/div[2]/div[1]/div[3]/table//tr/td/p[3]/span")
        time = 1
        for span in spans:
            # if time>3:
            #     break
            # time+=1
            content = span.xpath("text()").extract_first()
            print(content)
            result = re.match(r'\d+\.(.*?)(\d\d\d+).*?(\d*\.?\d*)%.*?(\d*)万', content)
            print(result.groups()[0])
            print(result.groups()[1])
            print(result.groups()[2])
            print(result.groups()[3])

            city = result.groups()[0]
            gdp = result.groups()[1]
            grouth = result.groups()[2]
            population = result.groups()[3]

            grouth = grouth if grouth else 0
            population = population if population else 0
            if city == '东营（山东8）':
                population = 213
            elif city =='成都（四川1）':
                population = 1591

            yield GDP(city=city, gdp=gdp, grouth=grouth, population=population)

        pass
