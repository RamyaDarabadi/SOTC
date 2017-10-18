"""This is Split crawler that gets data from Database"""
from scrapy.selector import Selector
from scrapy.spider import BaseSpider    
from scrapy.http import Request
import MySQLdb
class Sotc(BaseSpider):
    """Starts Name of the Crawler"""
    name = 'sotc_browse'
    def __init__(self):
        """Connecting to Database"""
        self.conn = MySQLdb.connect(
            host="localhost", user="root", passwd='01491a0237db', 
            db="sotcdb", charset='utf8', use_unicode=True)
        self.cur = self.conn.cursor()
    def start_requests(self):
        """Fetchs all rows"""
        qry = 'select title,image,link,price from sotc'
        self.cur.execute(qry)
        rows = self.cur.fetchall()
        for row in rows:
            """Starts yield request"""
            title, image, link, price = row 
            yield Request(link, callback=self.parse_place, meta={'image':image, 'title':title, 'link':link, 'price':price})
    def parse_place(self, response):
        """extracting data from Nodes"""
        sel = Selector(response)
        image = response.meta['image']
        place = response.meta['title']
        link = response.meta['link']
        price = response.meta['price']
        nodes = sel.xpath('//div[@class="jcarousel"]/ul/li//div[@class="border_gray"]')
        prices = []
        for node in nodes:
            """Starts xpaths for wanted information"""
            title = "".join(node.xpath(
                './/div[@class="col-lg-12 no-padding"]//h3[@class="package_h3"]/text()').extract())
            image = "".join(node.xpath(
                './/div[@class="col-lg-12 no-padding"]/a/img/@src').extract())
            link = "".join(node.xpath('.//div[@class="col-lg-12 no-padding"]/a/@href').extract())
            link = 'https://www.sotc.in'+link
            price = "".join(node.xpath(
                './/div[@class="col-lg-12 no-padding margin10"]//div[@class="col-md-6 col-xs-6 no-padding text_skyblue font22"]/text()').extract())
            if price:
                price = int(price.replace(',', '').replace('Rs.', ''))
            else:
                price = 0
            prices.append(price)
        if len(prices) >= 1:
            min_price = sorted(prices)[0]
        else:
            min_price = 0
        qry = 'insert into sotc(title,link,image,price)values(%s, %s, %s, %s)on duplicate key update title = %s, link = %s'
        values = (title, link, image, price, title, link)
        print qry%values
        self.cur.execute(qry, values)
        self.conn.commit()
