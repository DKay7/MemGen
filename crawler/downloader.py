import os
import httplib2
import pandas as pd
from PIL import Image
from tqdm import tqdm
from ast import literal_eval

h = httplib2.Http('.cache')
IMAGES_PATH = 'images'
TEMPLATES_PATH = 'templates'

DATA_PATH = 'memes_dataset.csv'
TEMPLATES_DATA_PATH = 'templates_memes_dataset.csv'


def download_image(url, img_name, path):
    if not os.path.isfile(os.path.join(IMAGES_PATH, img_name)):
        response, content = h.request(url)

        with open(os.path.join(path, img_name), 'wb') as file:
            file.write(content)


def get_dataset(templates=False):
    df = pd.read_csv(DATA_PATH)

    query = (df['image_alt'].map(lambda element: literal_eval(element).get('caption', None) is None)) & \
            (df['image_desc'].isna())

    df = df.drop(df[query].index)
    df.reset_index(drop=True, inplace=True)
    query = df['image_desc'].isna()
    df.loc[query, 'image_desc'] = df.loc[query, 'image_alt'].map(lambda element: element['caption'])
    df.to_csv(DATA_PATH, index=False)

    if templates:
        query = (df['template_url'].isna()) | (df['template_url'] == '')
        df.drop(df[query].index, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.to_csv(TEMPLATES_DATA_PATH, index=False)

        for index in tqdm(df.index):
            url = df.loc[index]['template_url']
            download_image(url, url.split('/')[-1], TEMPLATES_PATH)

    else:
        for index in tqdm(df.index):
            url = df.loc[index]['image_url']
            download_image(url, url.split('/')[-1], IMAGES_PATH)


def compress_images(templates=False):
    if templates:
        data_path = TEMPLATES_DATA_PATH
        target_column = 'template_url'
        images_path = TEMPLATES_PATH
    else:
        data_path = DATA_PATH
        target_column = 'image_url'
        images_path = IMAGES_PATH

    df = pd.read_csv(data_path)

    broken_files = 0

    for index in tqdm(df.index, total=len(df.index)):
        url = df.loc[index][target_column]
        img_name = url.split('/')[-1]

        try:
            img = Image.open(os.path.join(images_path, img_name)).convert('RGB')
            img.save(os.path.join(images_path, img_name), 'JPEG', dpi=[100, 100], quality=40)

        except BaseException as e:
            print(f'\nerror reading {img_name}: {e}')

            query = df[target_column].map(lambda x: x.split('/')[-1] == img_name)

            df.drop(df[query].index, inplace=True)
            df.reset_index(drop=True, inplace=True)

            os.remove(os.path.join(images_path, img_name))
            broken_files += 1

    print(f'\nTotal broken files: {broken_files}')
    df.to_csv(data_path, index=False)


if __name__ == '__main__':
    get_dataset(templates=True)
    compress_images(templates=True)
