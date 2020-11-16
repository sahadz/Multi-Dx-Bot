from pyrogram import filters, Client
from pyrogram.types import Message

@Client.on_message(filters.command("start", prefixes=["/"]))
async def start_message_handler(c: Client, m: Message):
        await m.reply_text(
            text=f"Hello! My name is Multi-DX😜"
        )
