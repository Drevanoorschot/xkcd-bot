import io
import sys

import discord
from discord import File, Guild
from discord.ext import commands, tasks
import requests
import logging

from config import config

# logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('xkcd-bot')
logger.setLevel(logging.INFO)

# file logger
file_log_handler = logging.FileHandler(filename='xkcd-bot.log', encoding='utf-8', mode='w')
file_log_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(file_log_handler)


# standard output logger
# print_log_handler = logging.StreamHandler(sys.stdout)
# print_log_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(print_log_handler)


class CheckerCog(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.index = 0
        self.bot = bot
        self.post_channel = 'xkcd'
        self.post_checker = PostChecker()
        self.post_checker_routine.start()

    def cog_unload(self):
        self.post_checker_routine.cancel()

    @tasks.loop(minutes=15)
    async def post_checker_routine(self):
        if self.post_checker.check_new():
            logger.log(logging.INFO, "new post! posting to all servers...")
            self.post_checker.update_last_and_store()
            img = io.BytesIO(requests.get(self.post_checker.last_comic_url).content)
            img_file = File(img, "comic.png")
            for server in self.bot.guilds:
                for channel in server.text_channels:
                    if channel.name == self.post_channel:
                        logger.log(logging.INFO, 'making post in {}'.format(server.name))
                        await channel.send(file=img_file)

    @post_checker_routine.before_loop
    async def before_post_checker(self):
        logger.log(logging.INFO, 'waiting for bot to be up...')
        await self.bot.wait_until_ready()
        logger.log(logging.INFO, 'all setup and ready to go!')


class PostChecker():
    def __init__(self):
        self.last_comic_url = self.get_url_from_store()

    def check_new(self) -> bool:
        last_comic_url = self._get_comic_url()
        return last_comic_url != self.last_comic_url

    def update_last_and_store(self):
        last_comic_url = self._get_comic_url()
        store = open('store.txt', 'w')
        store.write(last_comic_url)
        store.close()
        self.last_comic_url = last_comic_url

    @staticmethod
    def get_url_from_store() -> str:
        store = open('store.txt')
        last_comic_url = store.readline()
        store.close()
        return last_comic_url

    @staticmethod
    def _get_comic_url() -> str:
        page = requests.get('https://xkcd.com/').text
        return page.split('Image URL (for hotlinking/embedding): ')[1].split('<div')[0].replace('\n', '')


client = discord.Client()


@client.event
async def on_ready():
    logger.log(logging.INFO, 'We have logged in as {0.user}'.format(client))


@client.event
async def on_guild_join(server: Guild):
    logger.log(logging.INFO, "new Server joined: {}".format(server.name))
    text_channels = set(map(lambda x: x.name, server.text_channels))
    if 'xkcd' not in text_channels:
        logger.log(logging.INFO, 'xkcd channel non existent, creating xkcd channel...')
        await server.create_text_channel('xkcd')


CheckerCog(client)
client.run(config['token'])
