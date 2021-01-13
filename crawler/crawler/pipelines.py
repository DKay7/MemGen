# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas as pd
from itemadapter import ItemAdapter


class CrawlerPipeline:
    def __init__(self):
        self.memes_df = pd.DataFrame(columns=['image_url',
                                              'template_url',
                                              'image_alt',
                                              'image_desc'])

    def add_to_df(self, item):
        self.memes_df.loc[-1] = ItemAdapter(item).asdict()
        self.memes_df.index += 1

    def process_item(self, item, spider):
        self.add_to_df(item)

    def close_spider(self, spider):
        query = (self.memes_df['image_alt'].map(lambda element: literal_eval(element).get('caption', None) is None)) & \
                (self.memes_df['image_desc'].isna())

        self.memes_df = self.memes_df.drop(df[query].index)
        self.memes_df.reset_index(drop=True, inplace=True)

        query = self.memes_df['image_desc'].isna()
        df.loc[query, 'image_desc'] = df.loc[query, 'image_alt'].map(lambda element: element['caption'])

        self.memes_df.to_csv('memes_dataset.csv', sep=',', encoding='utf-8', index=False)

