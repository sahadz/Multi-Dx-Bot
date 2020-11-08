from config import Config
from pyrogram import filters
from pyrogram.types import Message
from multidxbot import MultiDxBot
from tools.utils import get_media_info, download_file


@MultiDxBot.on_message(filters.command("extractmediainfo") & filters.private & filters.incoming)
async def _(c: MultiDxBot, m: Message):
    if m.reply_to_message is None:
        await m.reply_text("Reply to message with this command", reply_to_message_id=m.message_id)
        return
    else:
        download_location = Config.DOWNLOAD_LOCATION
        msg_id = m.reply_to_message.message_id
        msg = await m.reply_text("Downloading your file", reply_to_message_id=m.message_id)
        file_location = await download_file(download_location, msg_id, m.chat.id, c)
        if file_location is None:
            await msg.edit("ERROR: Downloading failed")
        else:
            await msg.edit("Extracting Metadata of the file")
            media_file, media_link = await get_media_info(file_location)
            await c.send_chat_action(m.chat.id, "upload_document")
            await c.send_document(
                m.chat.id,
                media_file,
                reply_to_message_id=m.message_id,
                caption=f"Here is your Media Info file.\nIf you want to share it [click here]({media_link})",
                parse_mode="markdown"
            )