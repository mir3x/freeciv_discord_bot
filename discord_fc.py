import discord
import asyncio
import re

queue = []
dequeue = []

def read_token():
    with open("token.txt", "r") as f:
        line = f.readlines()
        return line[0].strip()


def stripmany(suffix, message):
    message = message.rstrip('\x00')
    if message.endswith(suffix):
        message = message[:len(message)-len(suffix)]

    message = message.rstrip('\x00')
    message = message.rstrip('[/c]')

    message = re.sub(r'\[c[^)]*\]', "",message)
    return message


@asyncio.coroutine
def handle_echo(reader, writer):
    global queue
    global dequeue
    data = yield from reader.read(600)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print("Received %r from %r" % (message, addr))
    i = message.find('::')
    sub = message[0:i+2]
    if (message and message != b'X' and message != sub and bytes(message, 'utf-8') != b'\x00'):
        message = stripmany(sub, message)
        queue.append(message)

    if len(dequeue):
        for tst in dequeue:
            t = tst.find(sub)
            print("FOUND?", t, sub, tst)
            if t != -1:
                rs = dequeue[t]
                x = rs
                dequeue.remove(x)
                print("send deque", rs)
                rs = rs.replace(sub, '')
                y = rs.encode()
                print("bytes:", bytes(y))
                writer.write(rs.encode())
    else:
        writer.write(b'')
        print("Wrote nothing")
    yield from writer.drain()
    writer.close()



class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        #channels where bot replies
        channels = ["bots", "commands", "lt55", "lt54"]
        valid_users = ["StarHelix#8062", "Fieder#7545", "Luas#4343"]
        if str(message.channel) in channels and str(message.author) in valid_users:
            if message.author == self.user:
                return

            if message.content == 'ping':
                await message.channel.send('pong')

            if message.content.startswith('!send'):
                rq = message.content
                rq = rq.replace('!send', '')
                print('Deque append', rq)
                dequeue.append(message.channel.name + '::' + rq)


    async def my_background_task(self):
        global queue
        await self.wait_until_ready()
        while not self.is_closed():
            if len(queue) > 0:
                msg = queue.pop(0)
                i = msg.find('::')
                sub = msg[0:i]
                channel = discord.utils.get(client.get_all_channels(), name=sub)
                if channel is not None:
                    await channel.send(msg)

            await asyncio.sleep(1) # task runs every 1 second

            #for channel in server.channels:
            #if channel.name == "Channel name":
            #break


print("Hello Discord")

loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo, '127.0.0.1', 9999, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    token = read_token()
    client = MyClient()
    client.run(token)
except KeyboardInterrupt:
    pass




