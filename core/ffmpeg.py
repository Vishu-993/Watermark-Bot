# (c) @AbirHasan2005

# This is Telegram Video Watermark Adder Bot's Source Code.
# I Hardly Made This. So Don't Forget to Give Me Credits.
# Done this Huge Task for Free. If you guys not support me,
# I will stop making such things!

# Edit anything at your own risk!

# Don't forget to help me if I done any mistake in the codes.
# Support Group: @JoinOT

import os
import math
import re
import json
import time
import shlex
import asyncio
from configs import Config
from typing import Tuple
from pyrogram.types import Message
from humanfriendly import format_timespan
from core.display_progress import TimeFormatter
from pyrogram.errors import FloodWait


from asyncio import create_subprocess_exec, sleep, subprocess
from math import floor
from os import path
from random import randint
from re import findall


async def add_watermark(input_path, output_path, text):
    try:
        ffmpeg.input(input_path).output(output_path, vf=f"drawtext=text='{text}':fontcolor=white:fontsize=24:x=10:y=10").run(overwrite_output=True)
        return True
    except ffmpeg.Error as e:
        print(f"ffmpeg error: {e.stderr}")
        return False
        

async def vidmark(
    the_media,
    message,
    watermark_path,
    output_vid,
    total_time,
    logs_msg,
    mode,
    position,
    size,
    user_id,
    public_log,
):
    num_threads = (
        (round(cpu_count() / 2) if round(cpu_count() / 2) == 0 else 1)
        if Vars.LIMIT_CPU
        else cpu_count()
    )
    working_dir = f"{Vars.DOWN_PATH}/{user_id}/progress.txt"
    file_genertor_command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "quiet",
        "-progress",
        working_dir,
        "-i",
        the_media,
        "-i",
        watermark_path,
        "-filter_complex",
        f"[1][0]scale2ref=w='iw*{size}/100':h='ow/mdar'[wm][vid];[vid][wm]overlay={position}",
        "-c:v",
        "h264",
        "-threads",
        str(num_threads),
        "-preset",
        mode,
        "-tune",
        "film",
        "-c:a",
        "copy",
        output_vid,
    ]
    process = await create_subprocess_exec(
        *file_genertor_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    LocalDB.set("pid", process.pid)
    cancel_kb = ikb([[("Cancel ❌", f"cancel_pid.{user_id}")]])

    try:
        while process.returncode != 0:
            await sleep(5)
            with open(working_dir, "r+") as file:
                text = file.read()
                frame = findall(r"frame=(\d+)", text)
                time_in_us = findall(r"out_time_ms=(\d+)", text)
                progress = findall(r"progress=(\w+)", text)
                speed = findall(r"speed=(\d+\.?\d*)", text)
                int(frame[-1]) if frame else 1
                speed = speed[-1] if speed else 1
                time_in_us = time_in_us[-1] if time_in_us else 1
                if progress and progress[-1] == "end":
                    break
                elapsed_time = int(time_in_us) / 1000000
                difference = floor((total_time - elapsed_time) / float(speed))
                eta = "-"
                if difference > 0:
                    eta = time_formatter(difference * 1000)
                percentage = floor(elapsed_time * 100 / total_time)
                progress_str = "📊 **Progress:** {}%\n`[{}{}]`".format(
                    round(percentage, 2),
                    "".join("▓" for _ in range(floor(percentage / 10))),
                    "".join("░" for _ in range(10 - floor(percentage / 10))),
                )

                stats = (
                    f"📦️ **Adding Watermark [Preset: `{mode}`]**\n\n"
                    f"⏰️ **ETA:** `{eta}`\n"
                    f"❇️ **Position:** `{position}`\n"
                    f"🔰 **PID:** `{process.pid}`\n🔄"
                    f"**Duration: `{format_timespan(total_time)}`**\n\n"
                    f"{progress_str}\n"
                )
                try:
                    await logs_msg.edit(text=stats, reply_markup=cancel_kb)
                    await public_log.edit(stats)
                    await message.edit(text=stats, reply_markup=cancel_kb)
                except MessageNotModified:
                    pass
                except FloodWait as e:
                    await sleep(e.value)
                except Exception as ef:
                    LOGGER.error(ef)
    except (FileNotFoundError, Exception):
        stats = "Adding watermark to Video, please wait..."
        try:
            await logs_msg.edit(text=stats, reply_markup=cancel_kb)
            await public_log.edit(stats)
            await message.edit(text=stats, reply_markup=cancel_kb)
        except MessageNotModified:
            pass
        except FloodWait as e:
            await sleep(e.value)
        except Exception as ef:
            LOGGER.error(ef)
            LOGGER.error(format_exc())
            return None

    _, stderr = await process.communicate()
    err_response = stderr.decode().strip()
    if err_response:
        LOGGER.error(err_response)
        return None
    if path.lexists(output_vid):
        return output_vid
    return None
    
        

async def take_screen_shot(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = output_directory + \
        "/" + str(time.time()) + ".jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name
    ]
    # width = "90"
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None
