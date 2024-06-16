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
import json
import re
import asyncio
import time
import subprocess
import time
import shlex
from psutil import cpu_count
from configs import Config
from humanfriendly import format_timespan
from core.display_progress import TimeFormatter
from pyrogram.errors.exceptions.flood_420 import FloodWait

num_threads = round(cpu_count() / 2) if round(cpu_count() / 2) > 0 else 1

async def vidmark(the_media, message, working_dir, watermark_path, output_vid, total_time, logs_msg, status, mode, position, size):
    file_generator_command = [
        "ffmpeg", "-hide_banner", "-loglevel", "quiet", "-progress", working_dir, "-i", the_media, "-i", watermark_path,
        "-filter_complex", f"[1][0]scale2ref=w='iw*{size}/100':h='ow/mdar'[wm][vid];[vid][wm]overlay={position}",
        "-c:v", "libx264", "-preset", mode, "-crf", "23", "-c:a", "copy", output_vid
    ]

    COMPRESSION_START_TIME = time.time()
    try:
        process = await asyncio.create_subprocess_exec(
            *file_generator_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        with open(status, 'r+') as f:
            statusMsg = json.load(f)
            statusMsg['pid'] = process.pid
            f.seek(0)
            json.dump(statusMsg, f, indent=2)

        while True:
            await asyncio.sleep(5)
            with open(working_dir, 'r') as file:
                text = file.read()
                frame = re.findall("frame=(\d+)", text)
                time_in_us = re.findall("out_time_ms=(\d+)", text)
                progress = re.findall("progress=(\w+)", text)
                speed = re.findall("speed=(\d+\.?\d*)", text)

                frame = int(frame[-1]) if frame else 1
                speed = float(speed[-1]) if speed else 1.0
                time_in_us = int(time_in_us[-1]) if time_in_us else 1

                if progress and progress[-1] == "end":
                    break

                execution_time = TimeFormatter((time.time() - COMPRESSION_START_TIME) * 1000)
                elapsed_time = time_in_us / 1000000
                difference = math.floor((total_time - elapsed_time) / speed)
                ETA = "-" if difference <= 0 else TimeFormatter(difference * 1000)
                percentage = min(100, math.floor(elapsed_time * 100 / total_time))

                progress_str = "📊 **Progress:** {0}%\n`[{1}{2}]`".format(
                    round(percentage, 2),
                    ''.join(["▓" for _ in range(math.floor(percentage / 10))]),
                    ''.join(["░" for _ in range(10 - math.floor(percentage / 10))])
                )
                stats = f'📦️ **Adding Watermark [Preset: `{mode}`]**\n\n' \
                        f'⏰️ **ETA:** `{ETA}`\n❇️ **Position:** `{position}`\n🔰 **PID:** `{process.pid}`\n🔄 **Duration: `{format_timespan(total_time)}`**\n\n' \
                        f'{progress_str}\n'

                try:
                    await logs_msg.edit(text=stats)
                    await message.edit(text=stats)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                except Exception as e:
                    print(f"Failed to update message: {e}")

        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
        print("FFmpeg stderr:", e_response)
        print("FFmpeg stdout:", t_response)

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, " ".join(file_generator_command))

        if os.path.exists(output_vid):
            return output_vid
        else:
            raise FileNotFoundError(f"Output video '{output_vid}' not found after FFmpeg execution.")

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        raise e
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
        raise e
    except Exception as e:
        print(f"Error in vidmark function: {e}")
        raise e
            



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
        
