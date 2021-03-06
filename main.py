import discord
import os
import requests
import main2

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$sentiment'):
        try:
            ticker = message.content.split(" ")[1]
            main2.create_sent_image([ticker])
            await message.channel.send(file=discord.File('analysis.png'))
        except:
            await message.channel.send('Error. Probably not a ticker.')


f = open(".env", 'r')
TOKEN = f.read()
print(TOKEN)
client.run(TOKEN)
