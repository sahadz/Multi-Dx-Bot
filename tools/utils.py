import time
import math
import asyncio
import aiohttp
import aiofiles
import json
import os
import logging
import secrets
from config import Config
from multidxbot import MultiDxBot
from pyrogram.types import Message
from pyrogram.errors import FloodWait


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


async def download_file(download_location: str, msg_id: int, edited_message: Message, chat_id: int, client: MultiDxBot):
    message = await client.get_messages(chat_id, msg_id)
    c_time = time.time()
    file_name = await get_filename(message)
    file_location = ""
    if file_name is None:
        return
    try:
        file_location = f"{download_location}/{file_name}"
        await message.download(
            file_location,
            progress=progress_pyrogram,
            progress_args=('download', edited_message, c_time)
        )
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


async def progress_pyrogram(
    current,
    total,
    ud_type,
    message,
    start
):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "Percentage: {0}%\nProgress: <code>[{1}{2}]</code>".format(
            round(percentage, 2),
            ''.join(["■" for i in range(math.floor(percentage / 5))]),
            ''.join(["□" for i in range(20 - math.floor(percentage / 5))])
        )

        curr_task = 'Downloading' if 'download' in ud_type else 'Uploading'

        tmp = "<b>{0} in progress</b>\nDone: {1} of {2}\nSpeed: {3}/s\nETA: {4}\n".format(
            curr_task,
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            # elapsed_time if elapsed_time != '' else "0 s",
            estimated_total_time if estimated_total_time != '' else "0 s"
        ) + progress
        try:
            await message.edit(
                text="{}".format(
                    tmp
                ),
                parse_mode="html"
            )

        except FloodWait as e:

            await asyncio.sleep(e.x)


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]
