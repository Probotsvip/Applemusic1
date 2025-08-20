import asyncio, httpx, os, re, yt_dlp
import logging

from typing import Union
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType
from youtubesearchpython.__future__ import VideosSearch

# Setup logger for YouTube API
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


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


async def get_stream_url(query, video=False):
    # Your custom API endpoint and parameters
    api_url = "https://nottyboyapii.jaydipmore28.workers.dev/youtube"
    api_key = "komal"
    
    logger.info(f"🎵 Starting stream URL request for: {query}")
    logger.info(f"📹 Request type: {'Video (MP4)' if video else 'Audio (MP3)'}")
    
    # Handle both video ID and full URL
    if len(query) == 11 and not query.startswith('http'):
        # It's a video ID, convert to full URL
        url = f"https://www.youtube.com/watch?v={query}"
        logger.info(f"🔄 Converted Video ID '{query}' to URL: {url}")
    else:
        # It's already a URL
        url = query
        logger.info(f"🔗 Using provided URL: {url}")
    
    logger.info(f"🌐 Sending request to API: {api_url}")
    
    async with httpx.AsyncClient(timeout=60, verify=False) as client:
        # Updated parameters for your API
        params = {"url": url, "apikey": api_key}
        logger.info(f"📋 Request parameters: url={url}, apikey={api_key}")
        
        try:
            response = await client.get(api_url, params=params)
            logger.info(f"📡 API Response Status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"❌ API returned error status: {response.status_code}")
                logger.error(f"❌ Response text: {response.text}")
                return ""
            
            # Parse your API response format
            info = response.json()
            logger.info(f"✅ API Response received successfully")
            logger.info(f"📊 Response data: Title={info.get('title', 'N/A')[:50]}...")
            logger.info(f"📊 Duration: {info.get('duration', 'N/A')}, Status: {info.get('status', 'N/A')}")
            logger.info(f"📊 Usage: {info.get('used', 0)}/{info.get('dailyLimit', 0)}")
            
            # Handle your API response structure with mp3 and mp4 URLs
            if video:
                # Return mp4 URL for video requests
                stream_url = info.get("mp4", "")
                if stream_url:
                    logger.info(f"✅ Video stream URL obtained (Length: {len(stream_url)} chars)")
                    logger.info(f"📹 Video Quality: {info.get('mp4Quality', 'Unknown')}")
                else:
                    logger.warning("⚠️ No MP4 URL found in response")
                return stream_url
            else:
                # Return mp3 URL for audio requests
                stream_url = info.get("mp3", "")
                if stream_url:
                    logger.info(f"✅ Audio stream URL obtained (Length: {len(stream_url)} chars)")
                    logger.info(f"🎵 Audio Quality: {info.get('mp3Quality', 'Unknown')}")
                else:
                    logger.warning("⚠️ No MP3 URL found in response")
                return stream_url
                
        except Exception as e:
            # Return empty string on any error to maintain compatibility
            logger.error(f"❌ Error during API request: {type(e).__name__}: {str(e)}")
            return ""


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
        if re.search(self.regex, link):
            return True
        else:
            return False

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
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        logger.info(f"📹 YouTubeAPI.video() called with link: {link}, videoid: {videoid}")
        
        if videoid:
            link = self.base + link
            logger.info(f"🔄 Converted to full URL: {link}")
            
        if "&" in link:
            link = link.split("&")[0]
            logger.info(f"🧹 Cleaned URL: {link}")
            
        logger.info("🚀 Calling get_stream_url for video...")
        result = await get_stream_url(link, True)
        logger.info(f"📹 YouTubeAPI.video() result: {'Success' if result else 'Failed'}")
        return result
        

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
        logger.info(f"⬇️ YouTubeAPI.download() called with link: {link}")
        logger.info(f"📋 Download parameters - video: {video}, videoid: {videoid}, songaudio: {songaudio}, songvideo: {songvideo}")
        
        if videoid:
            link = self.base + link
            logger.info(f"🔄 Converted video ID to URL: {link}")
            
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
            logger.info("🎬 Processing song video download...")
            await loop.run_in_executor(None, song_video_dl)
            fpath = f"downloads/{title}.mp4"
            logger.info(f"✅ Song video download completed: {fpath}")
            return fpath
        elif songaudio:
            logger.info("🎵 Processing song audio download...")
            await loop.run_in_executor(None, song_audio_dl)
            fpath = f"downloads/{title}.mp3"
            logger.info(f"✅ Song audio download completed: {fpath}")
            return fpath
        elif video:
            logger.info("📹 Getting video stream URL...")
            downloaded_file = await get_stream_url(link, True)
            direct = None
            logger.info(f"📹 Video stream result: {'Success' if downloaded_file else 'Failed'}")
        else:
            logger.info("🎵 Getting audio stream URL...")
            direct = None
            downloaded_file = await get_stream_url(link, False)
            logger.info(f"🎵 Audio stream result: {'Success' if downloaded_file else 'Failed'}")
            
        logger.info("✅ YouTubeAPI.download() completed")
        return downloaded_file, direct
