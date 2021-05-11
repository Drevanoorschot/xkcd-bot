import requests

from post import NewestPost, Post


class PostChecker:
    def __init__(self):
        self.page = requests.get('https://xkcd.com/').text
        self.post = NewestPost(self.page, self.get_url_from_store())

    def check_new(self) -> bool:
        self.update_page()
        link = self._get_comic_url()
        return link != self.post.link

    def update_post_to_latest_and_store(self):
        self.post = NewestPost(self.page, self._get_comic_url())
        store = open('store.txt', 'w')
        store.write(self.post.link)
        store.close()

    @staticmethod
    def get_url_from_store() -> str:
        store = open('store.txt')
        last_comic_url = store.readline()
        store.close()
        return last_comic_url

    def _get_comic_url(self) -> str:
        return self.page.split('Permanent link to this comic: ')[1].split('<br />')[0]

    def update_page(self):
        self.page = requests.get('https://xkcd.com/').text
