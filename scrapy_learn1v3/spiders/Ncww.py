# -*- coding: utf-8 -*-
import scrapy


class NcwwSpider(scrapy.Spider):
    name = 'Ncww'
    # start_urls = ['http://news.baidu.com/ns?word=V8+site%3Acww%2Enet%2Ecn&bs=V8+site%3Acww%2Enet%2Ecn&sr=0&cl=2&rn=20&tn=news&ct=0&clk=sortbytime']
    # start_urls = ['http://ajaxlist.it168.com/ChannelListAjaxHandler.ashx?type=channelList&channels=6&channelId=6&brandId=&typeId=-1&keyWords=&tabNames=&pageNum=22&isnewhtml=new&src=ajaxreturn&callbackparam=jQuery111305401495304392834_1517800310087&_=1517800310113']
    start_urls = ['http://ajaxlist.it168.com/ChannelListAjaxHandler.ashx?type=channelList&channels=6&channelId=6&brandId=&typeId=-1&keyWords=&tabNames=&pageNum=4&isnewhtml=new&src=ajaxreturn&callbackparam=jQuery111309110863950323809_1517798439511&_=1517798439522']

    def parse(self, response):
        print(response.text)
        pass


