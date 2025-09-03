import asyncio
import os
import re
import json
from typing import Union

import yt_dlp
import httpx   # ✅ added for API call
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from AviaxMusic.utils.database import is_on_off
from AviaxMusic.utils.formatters import time_to_seconds

import os
import glob
import random
import logging

# ===========================
# Logging setup
# ===========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

API_URL = "https://nottyboyapii.jaydipmore28.workers.dev/youtube"
API_KEY = "Nottyboy"

# ===========================
# API function for Stream URL
# ===========================
async def get_stream_url(query: str, video: bool = False):
    """
    Get YouTube stream URL (mp3/mp4) using Nottyboy API.
    query -> youtube link or video id
    video -> True for mp4, False for mp3
    """
    try:
        if len(query) == 11 and "http" not in query:
            youtube_url = f"https://youtube.com/watch?v={query}"
            logging.info("[get_stream_url] User ne Video ID diya: %s", query)
            logging.info("[get_stream_url] Converted to YouTube link: %s", youtube_url)
        else:
            youtube_url = query
            logging.info("[get_stream_url] User ne YouTube link diya: %s", youtube_url)

        params = {"url": youtube_url, "apikey": API_KEY}
        logging.info("[get_stream_url] Calling API: %s with params=%s", API_URL, params)

        async with httpx.AsyncClient(timeout=60, verify=False) as client:
            response = await client.get(API_URL, params=params)

        logging.info("[get_stream_url] API Response Status: %s", response.status_code)

        if response.status_code != 200:
            logging.error("[get_stream_url] API Error: %s", response.text)
            return ""

        data = response.json()
        logging.info("[get_stream_url] API Response JSON: %s", data)

        stream_url = data.get("mp4") if video else data.get("mp3")

        if not stream_url:
            logging.warning("[get_stream_url] Stream URL not found in response!")
            return ""

        logging.info("[get_stream_url] Final Stream URL: %s...", stream_url[:100])
        return stream_url

    except Exception as e:
        logging.exception("[get_stream_url] Exception: %s", str(e))
        return ""


# ===========================
# Cookies file selector
# ===========================
def cookie_txt_file():
    folder_path = f"{os.getcwd()}/cookies"
    filename = f"{os.getcwd()}/cookies/logs.csv"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    with open(filename, 'a') as file:
        file.write(f'Choosen File : {cookie_txt_file}\n')
    return f"""cookies/{str(cookie_txt_file).split("/")[-1]}"""


# ===========================
# File size checker
# ===========================
async def check_file_size(link):
    async def get_format_info(link):
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_txt_file(),
            "-J",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            print(f'Error:\n{stderr.decode()}')
            return None
        return json.loads(stdout.decode())

    def parse_size(formats):
        total_size = 0
        for format in formats:
            if 'filesize' in format:
                total_size += format['filesize']
        return total_size

    info = await get_format_info(link)
    if info is None:
        return None
    
    formats = info.get('formats', [])
    if not formats:
        print("No formats found.")
        return None
    
    total_size = parse_size(formats)
    return total_size


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


# ===========================
# YouTube API Class
# ===========================
class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return True if re.search(self.regex, link) else False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = 0 if str(duration_min) == "None" else int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]

    # ===========================
    # VIDEO STREAM URL (API ONLY)
    # ===========================
    async def video(self, link: str, videoid: Union[bool, str] = None):
        logging.info("[video()] called | input link=%s | videoid=%s", link, videoid)

        if videoid:
            link = self.base + videoid
            logging.info("[video()] videoid->link convert: %s", link)

        if "&" in link:
            old_link = link
            link = link.split("&")[0]
            logging.info("[video()] stripped extra params: %s -> %s", old_link, link)

        logging.info("[video()] calling get_stream_url(video=True)")
        stream_url = await get_stream_url(link, video=True)

        if stream_url:
            logging.info("[video()] API OK | returning stream_url")
            return 1, stream_url

        logging.error("[video()] API failed/no url")
        return 0, "Stream URL not found from API"

    # ===========================
    # PLAYLIST / TRACK / FORMATS
    # ===========================
    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_txt_file()} --playlist-end {limit} --skip-download {link}"
        )
        try:
            result = playlist.split("\n")
            result = [x for x in result if x]
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return {
                "title": result["title"],
                "link": result["link"],
                "vidid": result["id"],
                "duration_min": result["duration"],
                "thumb": result["thumbnails"][0]["url"].split("?")[0],
            }, result["id"]

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True, "cookiefile": cookie_txt_file()}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            r = ydl.extract_info(link, download=False)
            formats_available = []
            for format in r["formats"]:
                try:
                    if "dash" not in str(format["format"]).lower():
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format.get("filesize"),
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format.get("format_note"),
                                "yturl": link,
                            }
                        )
                except:
                    continue
        return formats_available, link

    # ===========================
    # SLIDER
    # ===========================
    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        return (
            result[query_type]["title"],
            result[query_type]["duration"],
            result[query_type]["thumbnails"][0]["url"].split("?")[0],
            result[query_type]["id"],
        )

    # ===========================
    # DOWNLOAD (API ONLY)
    # ===========================
    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        loop = asyncio.get_running_loop()

        if videoid:
            link = self.base + videoid
            logging.info("[download()] videoid->link convert: %s", link)

        if "&" in link:
            old_link = link
            link = link.split("&")[0]
            logging.info("[download()] stripped extra params: %s -> %s", old_link, link)

        if songvideo:
            logging.info("[download()] songvideo=True | API call")
            stream_url = await get_stream_url(link, video=True)
            return (stream_url, False) if stream_url else (None, False)

        elif songaudio:
            logging.info("[download()] songaudio=True | API call")
            stream_url = await get_stream_url(link, video=False)
            return (stream_url, False) if stream_url else (None, False)

        elif video:
            logging.info("[download()] video=True | API call")
            stream_url = await get_stream_url(link, video=True)
            return (stream_url, False) if stream_url else (None, False)

        else:
            logging.info("[download()] default=audio | API call")
            stream_url = await get_stream_url(link, video=False)
            return (stream_url, False) if stream_url else (None, False)
