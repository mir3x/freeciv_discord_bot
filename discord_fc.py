import discord
import asyncio

def read_token():
    with open("token.txt", "r") as f:
        line = f.readlines()
        return line[0].strip()


async def update_timeout():
    while not client.is_closed():
        print("sleeping ")
        #print timeout

        # wait 500 secs
        await asyncio.sleep(500)


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):

        #channels where bot replies
        channels = ["bots", "commands"]
        valid_users = ["StarHelix#8062", "Fieder#7545", "Luas#4343"]
        if str(message.channel) in channels and message.author in valid_users:
            if message.author == self.user:
                return

            if message.content == 'ping':
                await message.channel.send('pong')

print("Hello Discord")

token = read_token()
client = MyClient()
client.loop.create_task(update_timeout())
client.run(token)


