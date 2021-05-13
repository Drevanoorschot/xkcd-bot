import io
import json

import requests
from discord import File


class PostCheck:
    def __init__(self):
        info = json.loads(requests.get('https://xkcd.com/info.0.json').text)
        self.num = str(info['num'])
        self.title = info['title']
        self.alt = info['alt']
        self.img_link = info['img']
        self.link = f'https://xkcd.com/{self.num}/'
        self.img = None

    def is_new(self) -> bool:
        store = open('store.txt')
        latest = store.readline()
        store.close()
        return latest != self.num

    def update_store(self):
        store = open('store.txt', 'w')
        store.write(self.num)
        store.close()

    def set_image_bytes(self):
        self.img = requests.get(self.img_link).content

    def create_img_file(self) -> File:
        return File(io.BytesIO(self.img), self.title + '.png')