import scrapy
import logging
from tqdm import tqdm
from scrapy.exceptions import CloseSpider
from collections import defaultdict, Counter
from settings import MAX_MEMES_FOR_TEMPLATE, MAX_TEMPLATES, MAX_DESCRIPTION_LEN


pbar = tqdm(total=MAX_MEMES_FOR_TEMPLATE*MAX_TEMPLATES)

logging.getLogger('scrapy').propagate = False
logging.getLogger('PIL').setLevel(logging.WARNING)



class MemesSpider(scrapy.Spider):
    name = 'imgflip'
    start_urls = ['https://imgflip.com/memetemplates']

    memes_counter = Counter(defaultdict())
    template_counter = 0


    def parse(self, response, **kwargs):
        urls = response.xpath('//div[@class="mt-box"]/h3[@class="mt-title"]/a/@href').extract()

        for url in urls:
            url = response.urljoin(url)
            self.template_counter += 1

            if self.template_counter <= MAX_TEMPLATES:
                yield response.follow(url=url, callback=self.parse_memes_page)

            else:
                CloseSpider(reason='Max template number was reached')
                return

        next_page_xpath = '//div[@class="pager"]/a[@class="pager-next l but"]/@href'
        next_page = response.xpath(next_page_xpath).extract_first()

        if next_page:
            yield response.follow(url=next_page, callback=self.parse)

    def parse_memes_page(self, response):
        template_name_xpath = '//div[@id="page"]/h1/text()'
        template_name = response.xpath(template_name_xpath).extract_first()

        template_url_xpath = '//div[@id="base-right"]/div[@class="ibox"]/a[@class="meme-link"][1]/img/@src'
        template_url = response.xpath(template_url_xpath).extract_first()

        if (template_name and template_url):

            for a in response.xpath('//div[@class="base-unit clearfix"]/h2/a/@href').extract():
                if self.memes_counter[template_name] < MAX_MEMES_FOR_TEMPLATE:
                    template_url = response.urljoin(template_url)

                    yield response.follow(url=a, callback=self.parse_one_meme,
                                          cb_kwargs={'meme_template_name': template_name,
                                                     'meme_template_url': template_url})

                else:
                    return


            next_page_xpath = '//div[@class="pager"]/a[@class="pager-next l but"]/@href'
            next_page = response.xpath(next_page_xpath).extract_first()

            if next_page:
                yield response.follow(url=next_page, callback=self.parse_memes_page)


    def parse_one_meme(self, response, meme_template_name=None, meme_template_url=None):
        description = response.xpath('//div[@class="img-desc"]/text()').extract()
        description = ' '.join(description).strip()

        if description and len(description) <= MAX_DESCRIPTION_LEN and\
           self.memes_counter[meme_template_name] < MAX_MEMES_FOR_TEMPLATE:

            pbar.update(1)
            self.memes_counter[meme_template_name] += 1

            src = response.xpath('//img[@id="im"]/@src').extract_first()
            url = response.urljoin(src)

            yield {
                'meme_template_name': meme_template_name,
                'meme_template_url': meme_template_url,
                'meme_url': url,
                'meme_description': description,
                'template_path': None
            }

        else:
            return
