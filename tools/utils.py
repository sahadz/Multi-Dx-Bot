import asyncio
import aiohttp
import aiofiles
import json
import  os
import logging
import secrets
from config import Config
from multidxbot import MultiDxBot
from pyrogram.types import Message


async def get_media_info(file: str):
    neko_endpoint = "https://nekobin.com/api/documents"
    process_cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file]
    process = await asyncio.create_subprocess_exec(*process_cmd, stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)

    data, err = await process.communicate()
    m_info = json.loads(data.decode("utf-8").rstrip())

    if m_info is None:
        return False
    else:
        temp_file = os.path.join(Config.DOWNLOAD_LOCATION, f"{secrets.token_hex(2)}.txt")
        async with aiofiles.open(temp_file, mode="w") as m_file:
            await m_file.write(str(json.dumps(m_info, indent=2)))

        neko_link = ""

        async with aiohttp.ClientSession() as nekoSession:
            payload = {"content": str(json.dumps(m_info, indent=2))}
            async with nekoSession.post(neko_endpoint, data=payload) as resp:
                neko_link = f"https://nekobin.com/{(await resp.json())['result']['key']}.py"

    return temp_file, neko_link


async def download_file(download_location: str, msg_id: int, chat_id: int, client: MultiDxBot):
    message = await client.get_messages(chat_id, msg_id)
    file_name = await get_filename(message)
    file_location = ""
    if file_name is None:
        return
    try:
        file_location = f"{download_location}/{file_name}"
        await message.download(file_location)
    except Exception as e:
        logging.error(e)
        pass
    return file_location


async def get_filename(message: Message):
    if message.document is not None:
        return message.document.file_name
    elif message.video is not None:
        return message.video.file_name
    else:
        return None
