# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import re
import scrapy
from itemloaders.processors import MapCompose, Join


def common_text_preprocess(string):
    string = re.sub(r'\n', ' ', string.strip())
    string = re.sub(r'[^A-z!?.,:\";*~\']', ' ', string.strip()).strip()
    string = string.lower()

    return string


def urls_postprocess(url):
    if url is not None:
        url = " ".join(url)
        url = 'https:' + url

    return url


def alt_text_preprocess(string):
    string = " ".join(string)

    # Reversing because there're always last two values
    # and not always first two ones
    data = string.split('|')[::-1]

    # alt text have from 0 to 4 values,
    # so adding 4-len(alt text) None for save work
    data += [None] * max(0, 4 - len(data))

    if data[1] is not None:
        data[1] = data[1].replace('image tagged in', '').strip()
        data[1] = data[1].split(',')

    alt_fields = {'info': data[0],
                  'tags': data[1],
                  'caption': data[2],
                  'title': data[3],
                  }

    return alt_fields


class CrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    image_url = scrapy.Field(output_processor=urls_postprocess)
    template_url = scrapy.Field(output_processor=urls_postprocess)

    image_alt = scrapy.Field(input_processor=MapCompose(common_text_preprocess),
                             output_processor=alt_text_preprocess)

    image_desc = scrapy.Field(input_processor=MapCompose(common_text_preprocess),
                              output_processor=Join())
