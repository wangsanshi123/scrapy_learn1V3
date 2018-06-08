# -*- coding: utf-8 -*-
import datetime
from time import strftime, strptime, localtime

import scrapy

from scrapy_learn1v3.items import Mobilescout


class MobilescoutSpider(scrapy.Spider):
    name = 'mobilescout'
    start_urls = ['https://www.mobilescout.com/forum/forums/25-Samsung/']
    "https://www.mobilescout.com/forum/forums/25-Samsung/"
    "https://www.mobilescout.com/forum/forums/25-Samsung/page{}/"
    page = 1

    def start_requests(self):
        with open("mobilescout.txt") as f:
            for line in f.readlines():
                infos = line.split(",")
                brand = infos[0]
                url = infos[1]
                yield scrapy.Request(url=url, meta={"brand": brand, "url": url})

        pass

    def parse(self, response):
        brand = response.meta["brand"]
        url = response.meta["url"]

        lis = response.xpath(".//li[contains(@class,'threadbit')]")
        a = response.xpath(".//a[contains(@title,'Last Page')]")
        print("a:", a)
        if not a:
            # the last page
            return
            pass
        self.page += 1
        print("lis:", len(lis))
        time = 0
        for li in lis:
            # if time > 5:
            #     break
            # time += 1
            title = li.xpath(".//a[@class='title']/text()").extract_first()
            comment_url = li.xpath(".//a[@class='title']/@href").extract_first()
            author = li.xpath(".//a[@class='username understate']/text()").extract_first()
            # post_time = li.xpath(".//span[@class='label']/text()").extract_first()
            post_time = li.xpath(".//span[@class='label']").xpath("string()").extract_first()
            post_time = post_time.split(",")[1].strip() if post_time else ""
            print("post_time_before", post_time)
            post_time = self.dateFormat(post_time)

            reply = li.xpath(".//a[@class='understate']/text()").extract_first()
            view = li.xpath(".//div/ul/li[2]/text()").extract_first()
            view = view.replace("Views:", "").strip() if view else ""
            # print("title:", title)
            # print("author:", author)
            # print("post_time:", post_time)
            # print("reply:", reply)
            print("view:", view)
            # print("comment_url:", self.baseUrl + comment_url)
            yield Mobilescout(brand=brand, title=title, author=author, post_time=post_time, reply=reply, view=view,
                              comment_url=comment_url)

            pass

        # next  page
        yield scrapy.Request(url=url + "page{}/".format(self.page), meta={"brand": brand, "url": url})
        pass

    def dateFormat(self, date):
        "03-20-2018 05:13 PM"
        "Today 08:16 AM"
        "Yesterday 06:52 PM"
        if "Today" in date:
            date = strftime("%m-%d-%Y", localtime()) + date.replace("Today", "")

            pass
        elif "Yesterday" in date:
            now = datetime.datetime.today()
            delta = datetime.timedelta(days=-1)
            n_days = now + delta
            date = n_days.strftime('%m-%d-%Y') + date.replace("Yesterday", "")

            pass

        date = strftime("%Y-%m-%d %H:%M", strptime(date, "%m-%d-%Y %I:%M %p"
                                                         "")) if date else ""
        return date
        pass
