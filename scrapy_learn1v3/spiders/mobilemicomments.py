# -*- coding: utf-8 -*-
import json
import re
from time import localtime, strftime

import scrapy

from scrapy_learn1v3.items import MobileMiComment
from scrapy_learn1v3.utils.databaseUtil import MysqlUtil


class MobilemicommentsSpider(scrapy.Spider):
    name = 'mobilemicomments'
    "http://mobile.mi.com/in/max2/?RNType=product&product_id=max2#review"
    page = 0
    baseUrl = "http://m.buy.mi.com/in/comment/commentlist?product_id={}&orderby=0&pageindex={}&showimg=0&_=1521796496550&jsonpcallback=nextPage"

    # start_urls = [
    #     "http://m.buy.mi.com/in/comment/commentlist?product_id=max2&orderby=0&pageindex=0&showimg=0&_=1521796496550&jsonpcallback=nextPage"]

    def __init__(self):
        self.mysqlUtil = MysqlUtil()

    def start_requests(self):
        dataSet = self.mysqlUtil.select('mobilemi')
        time = 0
        for item in dataSet:
            # if time > 0:
            #     break
            # time += 1
            brand = item["brand"]
            model = item["model"]
            lastCommentDate = item["lastCommentdate"]
            product_id = item["product_id"]

            pageindex = 0

            comment_url = self.baseUrl.format(product_id, pageindex)

            print("comment_url:", comment_url)

            yield scrapy.Request(url=comment_url, meta={"brand": brand, "model": model, "pageindex": pageindex,
                                                        "product_id": product_id, "lastCommentDate": lastCommentDate})
        pass

    def parse(self, response):
        pageindex = response.meta["pageindex"]
        brand = response.meta["brand"]
        model = response.meta["model"]
        product_id = response.meta["product_id"]
        try:
            lastCommentDate = response.meta["lastCommentDate"]
        except:
            lastCommentDate = ""
        pageindex += 1
        ############format response##########################
        data = response.text
        data = re.search(r"nextPage(\(.*\))", data).groups()[0]
        data = data.replace("<br \/>\\n", "")
        data = data.replace("\\", "")
        data = re.sub("\s", " ", data)
        try:
            data = json.loads(data[1:len(data) - 1])
        except:
            # 直接解析下一页
            comment_url = self.baseUrl.format(product_id, pageindex)
            yield scrapy.Request(url=comment_url,
                                 meta={"brand": brand, "model": model, "pageindex": pageindex,
                                       "product_id": product_id})
            return
            pass
        ###############format response##########################
        errmsg = data["errmsg"]

        # the last page
        if errmsg != "Success":
            print("====lastPage=====:", pageindex)
            return

        comments = data['data']['comments']
        time = 0
        for comment in comments:
            time += 1
            comment_id = comment["comment_id"]
            author = comment["user_name"]
            score = comment["total_grade"]
            post_time = comment["add_time"]
            dt = localtime(float(post_time))
            post_time = strftime("%Y-%m-%d %H:%M:%S", dt)
            content = comment["comment_content"]
            likes = comment["up_num"]
            comment_num = comment["user_reply_num"]

            print("comment_id:", comment_id)
            print("author:", author)
            print("score:", score)
            print("post_time:", post_time)
            print("content:", content)
            print("likes:", likes)
            print("comment_num:", comment_num)

            print("==================")
            #####################增量更新########################################

            if post_time and post_time.strip() and lastCommentDate and str(lastCommentDate) >= post_time:  # 用于增量更新
                print("=====increasing update====", post_time)
                return

            # 记录下最新评论的时间
            if time == 1:
                self.mysqlUtil.cur.execute("update mobilemi set lastCommentDate=%s where product_id=%s",
                                           (post_time, product_id))
                self.mysqlUtil.conn.commit()
            ######################增量更新###################################

            yield MobileMiComment(comment_id=comment_id, brand=brand, model=model, author=author, score=score,
                                  post_time=post_time,
                                  content=content, likes=likes,
                                  comment_num=comment_num)

        # the next page
        comment_url = self.baseUrl.format(product_id, pageindex)
        yield scrapy.Request(url=comment_url,
                             meta={"brand": brand, "model": model, "pageindex": pageindex, "product_id": product_id})
        pass
