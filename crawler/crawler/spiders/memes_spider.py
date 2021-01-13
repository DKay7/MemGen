import scrapy
import logging
from tqdm import tqdm
from ..items import CrawlerItem
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

logging.getLogger('scrapy').propagate = False
pbar = tqdm()


class MemesSpider(CrawlSpider):
    name = 'imgflip_spider'
    start_urls = []

    for page in range(1, 130988):
        start_urls.append(f'https://imgflip.com/?sort=top-2020&page={page}')

    rules = (
        Rule(LinkExtractor(restrict_css='div.base-img-wrap-wrap > div > a', allow=('/i/',)),
             callback='parse_meme_page'),
    )

    def parse_meme_page(self, response):
        pbar.update(1)
        loader = ItemLoader(item=CrawlerItem(), response=response)

        loader.add_css('image_url', '#im::attr(src)')
        loader.add_css('template_url', '#img-main > a > img::attr(src)')
        loader.add_css('image_alt', '#im::attr(alt)')
        loader.add_css('image_desc', 'div.img-desc::text')

        yield loader.load_item()
