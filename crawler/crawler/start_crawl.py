import shutil
from scrapy.crawler import CrawlerProcess
from spiders.memes_spider import MemesSpider
from scrapy.utils.project import get_project_settings
from settings import IMAGES_STORE

process = CrawlerProcess(get_project_settings())
process.crawl(MemesSpider)
process.start()

shutil.make_archive(IMAGES_STORE, 'zip', IMAGES_STORE)
