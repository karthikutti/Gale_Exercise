# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urljoin
import threading
import requests
from bs4 import BeautifulSoup
from main.models import ScrapyItem
import json

class CrawlerThread(threading.Thread):
    def __init__(self, semaphore, url, crawlDepth, unique_id):
        self.semaphore = semaphore
        self.url = url
        self.crawlDepth = crawlDepth
        self.unique_id = unique_id
        self.threadId = hash(self)
        threading.Thread.__init__(self)

    def run(self):
        count = 0
        imgTags = []
        links = []
        source_code = requests.get(self.url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text)

        for link in soup.findAll('a', href=True):
            links.append(link['href'])

        for link in soup.findAll('img'):
            if 'src' in link.attrs:
                imgTags.append(link['src'])

        self.semaphore.acquire()
        urls = []
        images =[]
        for link in links:
            link = urljoin(self.url, link)
            urls.append(link)
        for img in imgTags:
            img = urljoin(self.url, img)
            images.append(img)
        item = ScrapyItem()
        item.unique_id = self.unique_id
        item.link_url = json.dumps(list(set(urls)))
        item.image_urls = json.dumps(list(set(images)))
        item.url = self.url
        item.save()
        self.semaphore.release()

        for url in urls:
            if self.crawlDepth > 1:
                CrawlerThread(self.semaphore, url, self.crawlDepth - 1, self.unique_id+str(count)).start()
                count=count+1

class IcrawlerSpider(CrawlSpider):
    name = 'icrawler'

    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url')
        self.depth = int(kwargs.get('depth'))
        self.unique_id = kwargs.get('unique_id')
        self.domain = kwargs.get('domain')
        self.start_urls = [self.url]
        self.allowed_domains = [self.domain]

        semaphore = threading.Semaphore(5)
        urls = [(self.url, self.depth)]
        for (url, crawlDepth) in urls:
            CrawlerThread(semaphore, url, crawlDepth, self.unique_id).start()

        super(IcrawlerSpider, self).__init__(*args, **kwargs)

    def parse_item(self, response):
        pass
