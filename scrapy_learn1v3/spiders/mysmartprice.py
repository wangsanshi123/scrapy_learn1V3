# -*- coding: utf-8 -*-
import scrapy

from scrapy_learn1v3.items import Mysmartprice


class MysmartpriceSpider(scrapy.Spider):
    name = 'mysmartprice'
    start_urls = ['http://www.mysmartprice.com/mobile/samsung-galaxy-s9-msp12867']

    def start_requests(self):
        with open("mysmartprice.txt") as f:
            for line in f.readlines():
                infos = line.split(",")
                brand = infos[0]
                model = infos[1]
                url = infos[2]
                yield scrapy.Request(url=url, meta={"brand": brand, "model": model})

        pass

    def parse(self, response):
        brand = response.meta["brand"]
        model = response.meta["model"]
        price = response.xpath(".//span[@class='prdct-dtl__prc-val']/text()").extract_first()
        price = price.replace(",", "") if price else ""
        temp = {}
        trs = response.xpath(".//tr[@class='tchncl-spcftn__item']")
        for item in trs:
            key = item.xpath(".//td[@class='tchncl-spcftn__item-key']/text()").extract_first()
            value = item.xpath(".//td[@class='tchncl-spcftn__item-val']").xpath("string()").extract_first()
            # print(key, ":", value)
            temp[key] = value
        size = temp["Size (in inches)"]
        rom = temp["Internal"]
        rom = rom.replace("GB", "") if rom else ""
        ram = temp["RAM"]
        ram = ram.replace("GB", "") if ram else ""
        battery = temp["Capacity"]
        battery = battery.replace("mAh", "") if battery else ""
        cpu = temp['Variant']

        score = response.xpath(
            ".//div[@class='usr-rvw__scr-cur']/text()").extract_first()
        comment_num = response.xpath(
            ".//div[@class='usr-rvw__rvwstr-rvws text-link js-open-link']/text()").extract_first()

        comment_num = comment_num.replace("reviews ➝", "").strip() if comment_num else ""
        comment_url = response.xpath(
            ".//div[@class='usr-rvw__rvwstr-rvws text-link js-open-link']/@data-open-link").extract_first()

        print("price:", price)
        print("size:", size)
        print("rom:", rom)
        print("ram:", ram)
        print("battery:", battery)
        print("cpu:", cpu)

        print("score:", score)
        print("comment_num:", comment_num)
        print("comment_url:", comment_url)
        yield Mysmartprice(brand=brand, model=model, price=price, size=size, rom=rom, ram=ram, battery=battery,
                           cpu=cpu,
                           score=score,
                           comment_num=comment_num,
                           comment_url=comment_url)
        print("=============================================================================================")
        pass
