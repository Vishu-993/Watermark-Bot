# (c) @AbirHasan2005

import time
from humanfriendly import format_timespan
from configs import Config
from core.display_progress import progress_for_pyrogram, humanbytes
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def send_video_handler(bot, cmd, output_vid, video_thumbnail, duration, width, height, editable, logs_msg, file_size):
    c_time = time.time()
    try:
        sent_vid = await bot.send_video(
            chat_id=cmd.chat.id,
            video=output_vid,
            caption=f"**File Name:** `{os.path.basename(output_vid)}`\n**Video Size:** `{humanbytes(file_size)}`\n**Duration:** `{format_timespan(duration)}`",
            thumb=video_thumbnail,
            width=width,
            height=height,
            duration=duration,
            supports_streaming=True,
            progress=progress_for_pyrogram,
            progress_args=(
                "Uploading Sir ...",
                editable,
                logs_msg,
                c_time
            )
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)
        sent_vid = await send_video_handler(bot, cmd, output_vid, video_thumbnail, duration, width, height, editable, logs_msg, file_size)
    except Exception as err:
        raise err
    return sent_vid
