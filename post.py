import io

import requests
from discord import File


class Post:
    def __init__(self):
        self.image_bytes: bytes
        self.title: str
        self.link: str


class NewestPost(Post):
    def __init__(self, page: str, link: str):
        super().__init__()
        self.page = page
        self.image_bytes = self.create_img_file()
        self.title = self.create_title()
        self.link = link

    def create_img_file(self) -> bytes:
        img_link = self.page.split('Image URL (for hotlinking/embedding): ')[1].split('\n')[0]
        return requests.get(img_link).content

    def create_title(self) -> str:
        return self.page.split('<div id=\"ctitle\">')[1].split('</div>')[0]

    def make_file(self) -> File:
        return File(io.BytesIO(self.image_bytes), self.title + '.png')