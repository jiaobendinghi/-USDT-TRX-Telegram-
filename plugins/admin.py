from pyrogram import Client, filters
from pyrogram import StopPropagation


# @Client.on_message(filters.user(users=5732433547) & filters.private)
# async def echo(client, message):
#     if message.text == "管理":
#         await message.reply("Hello, I'm a Pyrogram bot!")
#     # raise StopPropagation
#     # await message.reply(message.text)
