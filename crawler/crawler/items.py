# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


class CrawlerItem(scrapy.Item):
    meme_template_name = scrapy.Field()
    meme_template_url = scrapy.Field()

    meme_url = scrapy.Field()
    meme_description = scrapy.Field()

    template_path = scrapy.Field()

