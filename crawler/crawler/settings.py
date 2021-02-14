import os

MAX_MEMES_FOR_TEMPLATE = 7042
MIN_MEMES_FOR_TEMPLATE = 3000
MAX_TEMPLATES = 24
MAX_DESCRIPTION_LEN = 512

BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True


ITEM_PIPELINES = {
   'crawler.pipelines.CrawlerPipeline': 300,
   'crawler.pipelines.SaveImagesPipeline': 299,
}

IMAGE_QUALITY = 32
IMAGE_PATH = 'memes_templates'
IMAGES_STORE = os.path.join(os.path.dirname(__file__), IMAGE_PATH)

DATASET_PATH = os.path.join(os.path.dirname(__file__), 'memes_crawler.csv')
