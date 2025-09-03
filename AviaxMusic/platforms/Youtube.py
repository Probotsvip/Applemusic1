import asyncio
import os
import re
import json
from typing import Union

import httpx
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from AviaxMusic.utils.database import is_on_off
from AviaxMusic.utils.formatters import time_to_seconds

import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# New API URLs
AUDIO_API_URL = "https://jerrycoder.oggyapi.workers.dev/ytmp3"
VIDEO_API_URL = "https://jerrycoder.oggyapi.workers.dev/ytmp4"

async def get_stream_url(query: str, video: bool = False):
    """
    Get YouTube stream URL using JerryCoder API.
    query -> youtube link or video id
    video -> True for mp4, False for mp3
    """
    try:
        # Agar user ne sirf video id diya hai toh usko link me convert karo
        if len(query) == 11 and "http" not in query:
            youtube_url = f"https://youtube.com/watch?v={query}"
        else:
            youtube_url = query

        # Choose API URL based on video parameter
        api_url = VIDEO_API_URL if video else AUDIO_API_URL
        
        # API request banao
        params = {"url": youtube_url}
        logging.info(f"Calling API: {api_url} with params: {params}")

        async with httpx.AsyncClient(timeout=60, verify=False) as client:
            response = await client.get(api_url, params=params)

        logging.info(f"API Response Status: {response.status_code}")

        if response.status_code != 200:
            logging.error(f"API Error: {response.text}")
            return ""

        data = response.json()
        logging.info(f"API Response JSON: {data}")

        # Extract stream URL from response
        if video:
            # For video: data['result']['url']
            if data.get('status') and data.get('result', {}).get('url'):
                stream_url = data['result']['url']
            else:
                stream_url = ""
        else:
            # For audio: data['url'] 
            if data.get('status') and data.get('url'):
                stream_url = data['url']
            else:
                stream_url = ""

        if not stream_url:
            logging.warning("Stream URL not found in response!")
            return ""

        logging.info(f"Final Stream URL: {stream_url[:100]}...")
        return stream_url

    except Exception as e:
        logging.exception(f"Exception in get_stream_url: {str(e)}")
        return ""

# Baaki sab functions same rahenge...
# check_file_size, shell_cmd, etc. (cookies removed wale)

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    # ... other methods same ...

    async def video(self, link: str, videoid: Union[bool, str] = None, video: bool = False):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        # NAYA API USE KARO
        stream_url = await get_stream_url(link, video=video)
        return (1, stream_url) if stream_url else (0, "API Error: Stream URL not found")

    # ... baaki methods same ...

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
        )
        try:
            result = playlist.split("\n")
            for key in result:
                if key == "":
                    result.remove(key)
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
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    str(format["format"])
                except:
                    continue
                if not "dash" in str(format["format"]).lower():
                    try:
                        format["format"]
                        format["filesize"]
                        format["format_id"]
                        format["ext"]
                        format["format_note"]
                    except:
                        continue
                    formats_available.append(
                        {
                            "format": format["format"],
                            "filesize": format["filesize"],
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        }
                    )
        return formats_available, link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

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
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()
        
        def audio_dl():
            ydl_optssx = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def video_dl():
            ydl_optssx = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def song_video_dl():
            formats = f"{format_id}+140"
            fpath = f"downloads/{title}"
            ydl_optssx = {
                "format": formats,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            x.download([link])

        def song_audio_dl():
            fpath = f"downloads/{title}.%(ext)s"
            ydl_optssx = {
                "format": format_id,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            x.download([link])

        if songvideo:
            await loop.run_in_executor(None, song_video_dl)
            fpath = f"downloads/{title}.mp4"
            return fpath, True
        elif songaudio:
            await loop.run_in_executor(None, song_audio_dl)
            fpath = f"downloads/{title}.mp3"
            return fpath, True
        elif video:
            if await is_on_off(1):
                direct = True
                downloaded_file = await loop.run_in_executor(None, video_dl)
            else:
                # API se stream URL try karo pehle
                stream_url = await get_stream_url(link, video=True)
                if stream_url:
                    return stream_url, False
                else:
                    # Fallback to download
                    file_size = await check_file_size(link)
                    if not file_size:
                        print("None file Size")
                        return None, True
                    total_size_mb = file_size / (1024 * 1024)
                    if total_size_mb > 250:
                        print(f"File size {total_size_mb:.2f} MB exceeds the 100MB limit.")
                        return None, True
                    direct = True
                    downloaded_file = await loop.run_in_executor(None, video_dl)
        else:
            # Audio ke liye bhi API try karo pehle
            stream_url = await get_stream_url(link, video=False)
            if stream_url:
                return stream_url, False
            else:
                # Fallback to download
                direct = True
                downloaded_file = await loop.run_in_executor(None, audio_dl)
        
        return downloaded_file, direct

