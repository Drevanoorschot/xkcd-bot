import io

import discord
from discord import Guild
from discord.ext import commands, tasks

import logging

from config import config

# logging setup
from post_checker import PostCheck

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('xkcd-bot')
logger.setLevel(logging.INFO)

# file logger
file_log_handler = logging.FileHandler(filename='xkcd-bot.log', encoding='utf-8', mode='w')
file_log_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(file_log_handler)

class CheckerCog(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.index = 0
        self.bot = bot
        self.post_channel = 'xkcd'
        self.post_checker_routine.start()

    def cog_unload(self):
        self.post_checker_routine.cancel()

    @tasks.loop(minutes=15)
    async def post_checker_routine(self):
        postCheck = PostCheck()
        if postCheck.is_new():
            logger.log(logging.INFO, "new post! posting to all servers...")
            postCheck.update_store()
            postCheck.set_image_bytes()
            for server in self.bot.guilds:
                for channel in server.text_channels:
                    if channel.name == self.post_channel:
                        logger.log(logging.INFO, 'making post in {}'.format(server.name))
                        msg = await channel.send(file=postCheck.create_img_file(),
                                                 content='{title} ({link})'.format(
                                                     title=postCheck.title,
                                                     link=postCheck.link
                                                 ))
                        await msg.edit(suppress=True)
                        await channel.send(f'_{postCheck.alt}_')

    @post_checker_routine.before_loop
    async def before_post_checker(self):
        logger.log(logging.INFO, 'waiting for bot to be up...')
        await self.bot.wait_until_ready()
        logger.log(logging.INFO, 'all setup and ready to go!')


client = commands.Bot(command_prefix='!xkcd ')


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


@commands.command(name='source', help='Get a link to the source code of me')
async def source(ctx):
    await ctx.send('You can find my source code on GitHub: https://github.com/Drevanoorschot/xkcd-bot')


CheckerCog(client)

client.add_command(source)
client.run(config['token'])
