from pyrogram import filters

from pyrogram.types import Message

from multidxbot import MultiDxBot

@MultiDxBot.on_message(filters.command("start", prefixes=["/"]))

async def start_message_handler(c: Client, m: Message):

        await m.reply_text(

            text=f"Hello! My name is Multi-DX😜"

        )
