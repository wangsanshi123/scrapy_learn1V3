# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyLearn1V2Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AmazonPhoneInfo(scrapy.Item):
    brand = scrapy.Field()
    model = scrapy.Field()

    asin = scrapy.Field()  # 亚马逊商品唯一标识符
    price = scrapy.Field()
    score = scrapy.Field()
    comment_num = scrapy.Field()
    sellers_num = scrapy.Field()
    ram = scrapy.Field()
    weight = scrapy.Field()
    dimensions = scrapy.Field()

    colour = scrapy.Field()
    battery = scrapy.Field()
    special_features = scrapy.Field()
    available = scrapy.Field()
    best_sellers_rank = scrapy.Field()
    comment_url = scrapy.Field()

    isFocus = scrapy.Field()  # 是否关注
    lastDate = scrapy.Field()  # 上次更新时间
    isContentUpdated = scrapy.Field()  # 评论是否更新


class AmazonPhoneComment(scrapy.Item):
    brand = scrapy.Field()
    model = scrapy.Field()
    asin = scrapy.Field()
    score = scrapy.Field()
    author = scrapy.Field()

    date = scrapy.Field()
    content = scrapy.Field()
    unique_asin_author_content = scrapy.Field()  # 去除重复评论
    digg_num = scrapy.Field()


class Complaintboard(scrapy.Item):
    url = scrapy.Field()
    date = scrapy.Field()
    keyword = scrapy.Field()


class ComplaintboardComments(scrapy.Item):
    author = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()


class GDP(scrapy.Item):
    city = scrapy.Field()
    gdp = scrapy.Field()
    grouth = scrapy.Field()
    population = scrapy.Field()


class TwitterAccount(scrapy.Item):
    acount_name = scrapy.Field()
    twitter_num = scrapy.Field()
    following = scrapy.Field()
    followers = scrapy.Field()
    likes = scrapy.Field()
    place = scrapy.Field()


class TwitterText(scrapy.Item):
    acount_name = scrapy.Field()
    reply = scrapy.Field()
    retweet = scrapy.Field()
    likes = scrapy.Field()
    id = scrapy.Field()
    content = scrapy.Field()
    post_time = scrapy.Field()
    isContentUpdated = scrapy.Field()

    pass


class TwitterDetails(scrapy.Item):
    id = scrapy.Field()
    post_time = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    unique_posttime_author_content = scrapy.Field()

    pass


class MobileMi(scrapy.Item):
    "机型信息"
    brand = scrapy.Field()
    model = scrapy.Field()
    product_id = scrapy.Field()
    configure = scrapy.Field()
    comment_url = scrapy.Field()
    lastCommentdate = scrapy.Field()  # 上次最新评论时间

    pass


class MobileMiComment(scrapy.Item):
    "机型评论信息"
    comment_id = scrapy.Field()
    brand = scrapy.Field()
    model = scrapy.Field()
    author = scrapy.Field()

    score = scrapy.Field()
    post_time = scrapy.Field()
    content = scrapy.Field()
    likes = scrapy.Field()
    comment_num = scrapy.Field()

    pass


class Bhonko(scrapy.Item):
    author = scrapy.Field()
    post_time = scrapy.Field()
    seller = scrapy.Field()
    problem = scrapy.Field()

    detail = scrapy.Field()

    pass


class Mysmartprice(scrapy.Item):
    brand = scrapy.Field()
    model = scrapy.Field()
    price = scrapy.Field()
    size = scrapy.Field()
    rom = scrapy.Field()
    ram = scrapy.Field()
    battery = scrapy.Field()
    cpu = scrapy.Field()
    score = scrapy.Field()
    comment_num = scrapy.Field()
    comment_url = scrapy.Field()

    pass


class MysmartpriceComments(scrapy.Item):
    brand = scrapy.Field()
    model = scrapy.Field()
    author = scrapy.Field()
    post_time = scrapy.Field()
    likes = scrapy.Field()
    topic = scrapy.Field()
    content = scrapy.Field()
    star = scrapy.Field()
    pass


class Mobilescout(scrapy.Item):
    brand = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    post_time = scrapy.Field()
    reply = scrapy.Field()
    view = scrapy.Field()
    comment_url = scrapy.Field()

    pass


class Mobilescoutcomments(scrapy.Item):
    brand = scrapy.Field()
    title = scrapy.Field()
    post_time = scrapy.Field()
    author = scrapy.Field()
    author_title = scrapy.Field()
    join_time = scrapy.Field()
    posts = scrapy.Field()
    content = scrapy.Field()
    pass


class Bgr(scrapy.Item):
    "新闻概要"
    title = scrapy.Field()
    post_time = scrapy.Field()
    author = scrapy.Field()
    content_url = scrapy.Field()
    isContentUpdated = scrapy.Field()  # 判断新闻内容是否爬取

    pass


class BgrContent(scrapy.Item):
    "新闻内容"
    title = scrapy.Field()
    content = scrapy.Field()
