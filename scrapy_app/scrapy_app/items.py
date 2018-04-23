# -*- coding: utf-8 -*-
import scrapy


class ScrapyAppItem(scrapy.Item):
    link_url = scrapy.Field()
    images = scrapy.Field()
    image_urls = scrapy.Field()
