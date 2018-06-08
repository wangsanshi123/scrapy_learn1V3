# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy_learn1v3.items import AmazonPhoneInfo, AmazonPhoneComment, Complaintboard, ComplaintboardComments, GDP, \
    TwitterAccount, TwitterText, TwitterDetails, MobileMi, Bhonko, Mysmartprice, MysmartpriceComments, Mobilescout, \
    Mobilescoutcomments, Bgr, BgrContent, MobileMiComment
import pymysql


class ScrapyLearn1V3Pipeline(object):
    def process_item(self, item, spider):
        return item


import logging

from twisted.enterprise import adbapi

logger = logging.getLogger(__name__)


class MySQLStorePipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
        self.i = 0

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,

            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
        return cls(dbpool)

    # pipeline默认调用
    def process_item(self, item, spider):
        if isinstance(item, AmazonPhoneInfo):
            d = self.dbpool.runInteraction(self._process_AmazonPhoneInfo, item, spider)
        elif isinstance(item, AmazonPhoneComment):
            d = self.dbpool.runInteraction(self._process_AmazonPhoneComment, item, spider)
        elif isinstance(item, Complaintboard):
            d = self.dbpool.runInteraction(self._process_Complaintboard, item, spider)
        elif isinstance(item, ComplaintboardComments):
            d = self.dbpool.runInteraction(self._process_ComplaintboardComments, item, spider)

        elif isinstance(item, GDP):
            d = self.dbpool.runInteraction(self._process_Gdp, item, spider)
        elif isinstance(item, TwitterAccount):
            d = self.dbpool.runInteraction(self._process_TwitterAccount, item, spider)
        elif isinstance(item, TwitterText):
            d = self.dbpool.runInteraction(self._process_TwitterText, item, spider)
        elif isinstance(item, TwitterDetails):
            d = self.dbpool.runInteraction(self._process_TwitterDetail, item, spider)

        elif isinstance(item, MobileMi):
            d = self.dbpool.runInteraction(self._process_Mobilemi, item, spider)

        elif isinstance(item, MobileMiComment):
            d = self.dbpool.runInteraction(self._process_MobilemiComment, item, spider)



        elif isinstance(item, Bhonko):
            d = self.dbpool.runInteraction(self._process_Bhonko, item, spider)
        elif isinstance(item, Mysmartprice):
            d = self.dbpool.runInteraction(self._process_Mysmartprice, item, spider)

        elif isinstance(item, MysmartpriceComments):
            d = self.dbpool.runInteraction(self._process_Mysmartpricecomments, item, spider)

        elif isinstance(item, Mobilescout):
            d = self.dbpool.runInteraction(self._process_Mobilescout, item, spider)

        elif isinstance(item, Mobilescoutcomments):
            d = self.dbpool.runInteraction(self._process_Mobilescoutcomments, item, spider)
        elif isinstance(item, Bgr):
            d = self.dbpool.runInteraction(self._process_bgr, item, spider)
        elif isinstance(item, BgrContent):
            d = self.dbpool.runInteraction(self._process_bgrcontent, item, spider)



        else:
            d = self.dbpool.runInteraction(self._process_nothing, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d

    def _process_AmazonPhoneInfo(self, conn, item, spider):
        conn.execute("select * from amazon_phone_info where asin=%s", (item['asin'],))
        ret = conn.fetchone()

        try:
            if ret:
                conn.execute(
                    "update amazon_phone_info set comment_num=%s,score=%s,best_sellers_rank=%s,isFocus=%s,lastDate=%s where asin=%s",
                    (item['comment_num'], item['score'], item['best_sellers_rank'], item['isFocus'], item['lastDate'],
                     item['asin']))
                pass
            else:
                conn.execute(
                    "insert into amazon_phone_info VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (item['brand'], item['model'], item['asin'], item['price'], item['score'],
                     item['comment_num'], item['sellers_num'], item['ram'], item['weight'], item['dimensions'],
                     item['colour'], item['battery'], item['special_features'], item['available'],
                     item['best_sellers_rank'],
                     item['comment_url'], item['isFocus'], item['lastDate'], item['isContentUpdated']))
        except Exception as e:
            logger.error(e)
            pass

        pass

    def _process_AmazonPhoneComment(self, conn, item, spider):
        try:
            conn.execute("insert into amazon_phone_comment VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                         (item['brand'], item['model'], item['asin'], item['score'], item['author'], item['date'],
                          item['content'], item['unique_asin_author_content'], item['digg_num']))
        except Exception as e:
            logger.error(e)
            pass

        pass

    def _process_Complaintboard(self, conn, item, spider):
        conn.execute(" SELECT * FROM complaintboard  WHERE url =%s", (item['url'],))

        ret = conn.fetchone()
        if ret:
            return

        try:
            conn.execute("insert into complaintboard VALUES (%s,%s,%s)",
                         (item['keyword'], item['date'], item['url']))
        except Exception as e:
            logger.error(e)
            pass

        pass

    def _process_ComplaintboardComments(self, conn, item, spider):
        try:
            conn.execute("insert into complaintboardcomments VALUES (%s,%s,%s,%s)",
                         (item['author'], item['date'], item['title'], item['content']))
        except Exception as e:
            logger.error(e)
            pass

        pass

    def _process_Gdp(self, conn, item, spider):
        try:
            conn.execute("insert into gdp VALUES (%s,%s,%s,%s)",
                         (item['city'], item['gdp'], item['grouth'], item['population']))
        except Exception as e:
            logger.error(e)
            pass

        pass

    def _process_TwitterAccount(self, conn, item, spider):
        try:
            conn.execute("insert into twitter_account VALUES (%s,%s,%s,%s,%s,%s)",
                         (item['acount_name'], item['twitter_num'], item['following'], item['followers'], item['likes'],
                          item['place']))
        except Exception as e:
            logger.error(e)
            pass

        pass

    def _process_TwitterText(self, conn, item, spider):
        try:
            conn.execute("insert into twitter_text VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                         (item['acount_name'], item['reply'], item['retweet'], item['likes'], item['id'],
                          item['content'], item['post_time'], item['isContentUpdated']))
        except Exception as e:
            logger.error(e)
            pass

        pass

    def _process_TwitterDetail(self, conn, item, spider):
        try:
            conn.execute("insert into twitter_detail VALUES (%s,%s,%s,%s,%s)",
                         (item['id'], item['post_time'], item['content'], item['author'],
                          item['unique_posttime_author_content']))
        except Exception as e:
            logger.error(e)
            pass

        pass

    def _process_Mobilemi(self, conn, item, spider):
        try:
            conn.execute("select * from mobilemi where product_id=%s", (item['product_id'],))
        except Exception as e:
            logger.error(e)
            pass
        ret = conn.fetchone()
        if ret:
            # update
            conn.execute(
                "update mobilemi set brand=%s,model =%s,configure = %s, comment_url = %s,lastCommentdate=%s where =product_id%s",
                (item['brand'], item['model'], item['configure'], item['comment_url'], item['lastCommentdate'],
                 item['product_id']))

            pass
        else:
            try:
                conn.execute("insert into mobilemi VALUES (%s,%s,%s,%s,%s,%s)",
                             (item['brand'], item['model'], item["product_id"], item['configure'], item['comment_url'],
                              item["lastCommentdate"]))
            except Exception as e:
                logger.error(e)
        pass

    def _process_MobilemiComment(self, conn, item, spider):
        try:
            conn.execute("insert into mobilemicomments VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                         (item["comment_id"], item['brand'], item['model'], item['author'], item['score'],
                          item['post_time'], item['content'],
                          item['likes'], item['comment_num']))
        except Exception as e:
            logger.error(e)
            pass

    def _process_Bhonko(self, conn, item, spider):
        conn.execute("select * from bhonko where author=%s and post_time=%s", (item['author'], item["post_time"]))
        ret = conn.fetchone()
        if not ret:
            try:
                conn.execute("insert into bhonko VALUES (%s,%s,%s,%s,%s)",
                             (item['author'], item['post_time'], item['seller'], item['problem'], item["detail"]))
            except Exception as e:
                logger.error(e)
                pass

        pass

    def _process_Mysmartprice(self, conn, item, spider):
        conn.execute("select * from mysmartprice where comment_url=%s", (item['comment_url'],))
        ret = conn.fetchone()
        if not ret:
            try:
                conn.execute("insert into mysmartprice VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                             (item["brand"], item["model"], item['price'], item['size'], item['rom'], item['ram'],
                              item["battery"],
                              item["cpu"],
                              item["score"],
                              item["comment_num"],
                              item["comment_url"]))
            except Exception as e:
                logger.error(e)
                pass

        pass

    def _process_Mysmartpricecomments(self, conn, item, spider):
        try:
            conn.execute("insert into mysmartpricecomments VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                         (item["brand"], item["model"], item['author'], item['post_time'], item['likes'],
                          item['topic'],
                          item["content"],
                          item["star"],
                          ))
        except Exception as e:
            logger.error(e)
            pass

    def _process_Mobilescout(self, conn, item, spider):
        try:
            conn.execute("insert into mobilescout VALUES (%s,%s,%s,%s,%s,%s,%s)",
                         (item["brand"], item["title"], item["author"], item['post_time'], item['reply'], item['view'],
                          item['comment_url'],

                          ))
        except Exception as e:
            logger.error(e)
            pass

    def _process_Mobilescoutcomments(self, conn, item, spider):
        try:
            conn.execute("insert into mobilescoutcomments VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                         (item["brand"], item["title"], item["post_time"], item['author'], item['author_title'],
                          item['join_time'],
                          item['posts'],
                          item['content']

                          ))
        except Exception as e:
            logger.error(e)
            pass

    def _process_bgr(self, conn, item, spider):
        try:
            conn.execute("insert into bgr VALUES (%s,%s,%s,%s,%s)",
                         (
                             item["title"], item["post_time"], item['author'], item['content_url'],
                             item["isContentUpdated"]
                         ))
        except Exception as e:
            logger.error(e)
            pass

    def _process_bgrcontent(self, conn, item, spider):
        try:
            conn.execute("insert into bgrcontent VALUES (%s,%s)",
                         (item["title"], item["content"]
                          ))
        except Exception as e:
            logger.error(e)
            pass

    def _process_nothing(self, conn, item, spider):
        # do nothing

        pass
        # 异常处理

    def _handle_error(self, failure, item, spider):
        logger.error(failure)
