# -*- coding: utf-8 -*-
import re
from time import strptime, strftime, localtime

import scrapy

from scrapy_learn1v3.items import AmazonPhoneInfo
from scrapy_learn1v3.utils.amazonutils import getBrandModel, saveBrandIgnore


class AmazonSpider(scrapy.Spider):
    '搜索页面的结果被亚马逊封了，要求验证，所以只能用selenium的方式爬取'
    name = "amazon"

    baseUrl = 'https://www.amazon.in/s/ref=nb_sb_noss_2?url=node%3D1805560031&field-keywords={}&rh=n%3A976419031%2Cn%3A1389401031%2Cn%3A1389432031%2Cn%3A1805560031%2Ck%3A{}'
    'https://www.amazon.in/s/ref=nb_sb_noss?url=node%3D1805560031&field-keywords=vivo+Y55L&rh=n%3A1805560031%2Ck%3Avivo+Y55L'
    'https://www.amazon.in/s/ref=nb_sb_noss?url=node%3D1805560031&field-keywords=vivo+y66&rh=n%3A1805560031%2Ck%3Avivo+y66'
    headUrl = "https://www.amazon.in/"
    now = strftime("%Y-%m-%d", localtime())

    # "https://www.amazon.in/s/ref=nb_sb_noss_2?url=node%3D1805560031&field-keywords=vivo+Y55&rh=n%3A976419031%2Cn%3A1389401031%2Cn%3A1389432031%2Cn%3A1805560031%2Ck%3Avivo+Y55"
    def start_requests(self):
        time = 0
        for brand, model in getBrandModel():
            # if time > 0:
            #     break
            # time += 1

            keyword = brand + "+" + model
            url = self.baseUrl.format(keyword, keyword)
            print("url:", url)
            yield scrapy.Request(url=url)

        pass

    def parse(self, response):

        count = response.xpath(".//*[@id='s-result-count']/text()").extract_first()
        print("search_count:", count)
        count = str(count.split(" ")[0]) if count else 0
        if isinstance(count, str) and not count.strip("").isdigit():
            # 此种情况搜索结果过多，且大多为无用结果，所以排除
            return
            pass
        print("count:", count)
        print(response)
        # print("model:", model)
        # if count == 0:  # 有些情况下，搜索结果因为未知原因显示为零，但是实际不为零，此时保存brand,model用于重新爬取
        #     saveBrandIgnore(brand, model)

        for i in range(int(count)):
            url = response.xpath("//*[@id='result_{}']/div/div[3]/div[1]/a/@href".format(i)).extract_first()
            if url:
                yield scrapy.Request(url=url, meta={'url': url},
                                     callback=self.parseModel)
        pass

    def parseModel(self, response):
        "解析指定型号手机的搜索信息"
        url = response.meta["url"]
        # brand = response.xpath('.//*[@id="brand"]/text()').extract_first()

        # title = response.xpath(".//span[@id='productTitle']/text()").extract_first()
        title = response.xpath(".//h1[@id='title']").xpath("string()").extract_first()
        brand = title.strip().split(" ")[0] if title else ""
        model = " ".join(title.strip().split(" ")[1:]) if title else ""
        print("url:", url)
        # print("brand:", brand)
        # print("model:", model)

        price = response.xpath(".//*[@id='olp_feature_div']/div/span/span/text()").extract_first()
        comment_num = response.xpath(".//*[@id='acrCustomerReviewText']/text()").extract_first()

        price = float(price.replace(",", "")) if price else 0

        if not comment_num or price < 3000:
            return
        else:
            for phoneInfo in self.parseModelInfo(response, brand, model):
                yield phoneInfo

        pass

    def parseModelInfo(self, response, brand, model):
        "解析指定手机型号概要信息"
        dict_temp = {}
        print("===parseModelInfo===", response)
        score = response.xpath(".//*[@id='acrPopover']/span[1]/a/i[1]/span/text()").extract_first()
        comment_num = response.xpath(".//*[@id='acrCustomerReviewText']/text()").extract_first()
        sellers_num = response.xpath(".//*[@id='olp_feature_div']/div/span/a/text()").extract_first()
        price = response.xpath(".//*[@id='olp_feature_div']/div/span/span/text()").extract_first()

        total_items = len(response.xpath(".//*[@id='prodDetails']/div/div[1]/div/div[2]/div/div/table//tr"))

        for i in range(total_items - 1):
            item_name = response.xpath(
                ".//*[@id='prodDetails']/div/div[1]/div/div[2]/div/div/table//tr[{}]/td[1]/text()".format(
                    i + 1)).extract_first().strip()
            item_value = response.xpath(
                ".//*[@id='prodDetails']/div/div[1]/div/div[2]/div/div/table//tr[{}]/td[2]/text()".format(
                    i + 1)).extract_first().strip()
            dict_temp[item_name] = item_value
        try:
            ram = dict_temp['RAM']
        except:
            ram = 0
            pass
        try:
            dimensions = dict_temp['Product Dimensions']
        except:
            dimensions = 0
            pass
        try:
            weight = dict_temp['Weight']
        except:
            weight = 0
            pass
        try:
            special_features = dict_temp['Special features']
        except:
            special_features = ""
            pass
        try:
            colour = dict_temp['Colour']
        except:
            colour = ""
            pass
        try:
            battery = dict_temp['Battery Power Rating']
        except:
            battery = ""
            pass

        asin = response.xpath(
            ".//*[@id='prodDetails']/div/div[2]/div[1]/div[2]/div/div/table//tr[1]/td[2]/text()").extract_first()
        best_sellers_rank = response.xpath(".//*[@id='SalesRank']/td[2]/ul/li/span[1]/text()").extract_first()
        available = response.xpath(
            ".//*[@id='prodDetails']/div/div[2]/div[1]/div[2]/div/div/table//tr[4]/td[2]/text()").extract_first()
        comment_url = self.headUrl + response.xpath('//*[@id="acrCustomerReviewLink"]/@href').extract_first()
        score = score.split(" ")[0] if score else 0
        price = float(price.replace(",", "")) if price else 0
        sellers_num = re.search(r'(\d*)', sellers_num).groups()[0] if sellers_num else 0

        comment_num = comment_num.split(" ")[0] if comment_num else 0
        ram = ram.split(" ")[0] if ram else 0
        weight = weight.split(" ")[0] if weight else 0
        best_sellers_rank = best_sellers_rank.strip("#") if best_sellers_rank else 0
        try:
            available = strftime("%Y-%m-%d", strptime(available, "%d %B %Y"))
        except:
            available = ""
            pass

        print("brand:", brand)
        print("model:", model)

        # print("score:", score)
        # print("price:", price)
        # print("model:", model)
        # print("sellers_num:", sellers_num)
        # print("comment_num:", comment_num)
        # print("ram:", ram)
        # print("weight:", weight)
        # print("dimensions:", dimensions)
        # print("special_features:", special_features)
        # print("battery:", battery)
        # print("colour:", colour)
        # print("asin:", asin)
        # print("best_sellers_rank:", best_sellers_rank)
        # print("available:", available)
        # print("comment_url:", comment_url)

        yield AmazonPhoneInfo(brand=brand, model=model, asin=asin, price=price, score=score,
                              comment_num=comment_num, sellers_num=sellers_num, ram=ram, weight=weight,
                              dimensions=dimensions, colour=colour, battery=battery,
                              special_features=special_features, available=available,
                              best_sellers_rank=best_sellers_rank, comment_url=comment_url, isFocus=True,
                              lastDate=self.now, isContentUpdated=0)
        pass
