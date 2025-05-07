# ATLEAST GIVE CREDITS IF YOU STEALING :(((((((((((((((((((((((((((((((((((((
# ELSE NO FURTHER PUBLIC THUMBNAIL UPDATES

import random
import logging
import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch

logging.basicConfig(level=logging.INFO)

def create_thumbnail(thumbnail_url, title, uploader, duration, played, output_path): # Load thumbnail image from URL response = requests.get(thumbnail_url) thumb_image = Image.open(BytesIO(response.content)).convert("RGB")

# Resize and blur background
bg = thumb_image.resize((1280, 720)).filter(ImageFilter.GaussianBlur(radius=25))

# Dark overlay
overlay = Image.new('RGBA', bg.size, (0, 0, 0, 100))
bg.paste(overlay, (0, 0), overlay)

# Rounded thumbnail (small front image)
thumb_small = thumb_image.resize((400, 400))
mask = Image.new('L', (400, 400), 0)
draw_mask = ImageDraw.Draw(mask)
draw_mask.ellipse((0, 0, 400, 400), fill=255)
thumb_small.putalpha(mask)

# Paste rounded image at center-left
bg.paste(thumb_small, (80, 160), thumb_small)

draw = ImageDraw.Draw(bg)

# Fonts (use your path to font or system font)
title_font = ImageFont.truetype("arialbd.ttf", 60)
info_font = ImageFont.truetype("arial.ttf", 40)
small_font = ImageFont.truetype("arial.ttf", 35)

# Text positions
draw.text((520, 200), title, font=title_font, fill=(255, 255, 255))
draw.text((520, 280), f"{uploader}", font=info_font, fill=(200, 200, 200))

# Progress Bar background
progress_x = 520
progress_y = 400
progress_width = 650
progress_height = 15

draw.rectangle([progress_x, progress_y, progress_x + progress_width, progress_y + progress_height], fill=(80,80,80))

# Progress (played / duration)
if duration != 0:
    progress_percent = played / duration
else:
    progress_percent = 0

played_width = int(progress_width * progress_percent)

draw.rectangle([progress_x, progress_y, progress_x + played_width, progress_y + progress_height], fill=(255, 0, 0))

# Durations (current / total)
def sec_to_min(sec):
    mins = sec // 60
    secs = sec % 60
    return f"{int(mins)}:{int(secs):02}"

played_txt = sec_to_min(played)
duration_txt = sec_to_min(duration)

draw.text((520, 430), f"{played_txt}", font=small_font, fill=(255,255,255))
draw.text((1150, 430), f"{duration_txt}", font=small_font, fill=(255,255,255))

# Optional icons (pause, YT, speaker)—static placeholders
# (You can load PNG icons & paste like thumbnail if you want exact look)

# Save final image
bg.save(output_path)

Example call:

create_thumbnail(thumbnail_url, "Song Title", "Uploader Name", duration_seconds, played_seconds, "output.jpg")


