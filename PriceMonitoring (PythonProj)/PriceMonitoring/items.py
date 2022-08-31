# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PricemonitoringItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    linkraw = scrapy.Field()
    imgsrc = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    itemssold = scrapy.Field()
