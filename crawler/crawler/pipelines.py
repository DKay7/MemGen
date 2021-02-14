import os
import re
import scrapy
import pandas as pd
from PIL import Image
from io import BytesIO
from pathlib import Path
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from settings import MIN_MEMES_FOR_TEMPLATE, IMAGE_QUALITY, DATASET_PATH


class CrawlerPipeline:
    def __init__(self):
        self.memes_df = pd.DataFrame(columns=['meme_template_name',
                                              'meme_template_url',
                                              'meme_url',
                                              'meme_description',
                                              'template_path'])

    def clear_text(self, item):
        description = item.get('meme_description', None)
        template_name = item.get('meme_template_name', None)

        if description is not None:
            description = description.lower()
            description = re.sub(r'\n', ' ', description)
            description = re.sub(r'[^A-z0-9!?.,_\-;:* ] ', '', description)
            item['meme_description'] = description.strip()

        if template_name is not None:
            template_name = item['meme_template_name']
            template_name = template_name.lower()
            template_name = re.sub(r'\n', ' ', template_name)
            template_name = re.sub(r'[^A-z0-9_ ]', '', template_name).strip()
            template_name = template_name.replace(' ', '_')

        item['meme_template_name'] = template_name.strip()

        return item

    def process_item(self, item, spider):
        item = self.clear_text(item)
        self.memes_df = self.memes_df.append(ItemAdapter(item).asdict(), ignore_index=True)
        return item

    def close_spider(self, spider):
        query = (self.memes_df['meme_template_name'].isna()) | (self.memes_df['meme_description'].isna()) |  \
                (self.memes_df['template_path'].isna())

        self.memes_df.drop(self.memes_df[query].index, inplace=True)
        self.memes_df.reset_index(drop=True, inplace=True)

        counts = self.memes_df['meme_template_name'].value_counts().to_dict()

        for key, value in counts.items():
            if value < MIN_MEMES_FOR_TEMPLATE:
                query = (self.memes_df['meme_template_name'] == key)
                self.memes_df.drop(self.memes_df[query].index, inplace=True)

        self.memes_df.reset_index(drop=True, inplace=True)
        self.memes_df.to_csv(DATASET_PATH, sep=',', encoding='utf-8', index=False)

        print(f"Spider closed")
        print(f"Total unique templates: {self.memes_df['meme_template_name'].unique()}")


class SaveImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        template_name = item['meme_template_name']
        template_name = template_name.lower()
        template_name = re.sub(r'\n', ' ', template_name)
        template_name = re.sub(r'[^A-z0-9_ ]', '', template_name).strip()
        template_name = template_name.replace(' ', '_')


        _, extension = os.path.splitext(item['meme_template_url'])

        path = Path(template_name).with_suffix(extension)
        return str(path)

    def get_media_requests(self, item, info):
        if item:
            yield scrapy.Request(item['meme_template_url'])

    def convert_image(self, image, size=None):
        if image.format == 'PNG' and image.mode == 'RGBA':
            background = Image.new('RGBA', image.size, (255, 255, 255))
            background.paste(image, image)
            image = background.convert('RGB')

        elif image.mode == 'P':
            image = image.convert("RGBA")
            background = Image.new('RGBA', image.size, (255, 255, 255))
            background.paste(image, image)
            image = background.convert('RGB')

        elif image.mode != 'RGB':
            image = image.convert('RGB')

        if size:
            image = image.copy()
            image.thumbnail(size, Image.ANTIALIAS)

        buf = BytesIO()
        image.save(buf, 'JPEG', quality=IMAGE_QUALITY)

        return image, buf

    def item_completed(self, results, item, info):
        if item:
            downloaded_ok, result = results[0]

            if downloaded_ok:
                item['template_path'] = result['path']

            return item
