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

def generate_thumbnail(background_url, song_title, artist_name, duration, output_path="thumbnail.jpg"): # Fonts path (adjust if using custom fonts) FONT_BOLD = "arialbd.ttf" FONT_REGULAR = "arial.ttf"

# Load background image and blur it
response = requests.get(background_url)
bg_image = Image.open(BytesIO(response.content)).convert("RGB")
bg_image = bg_image.resize((1280, 720))
blurred_bg = bg_image.filter(ImageFilter.GaussianBlur(radius=15))

# Overlay a semi-transparent dark layer
overlay = Image.new('RGBA', blurred_bg.size, (0, 0, 0, 120))
blurred_bg = Image.alpha_composite(blurred_bg.convert("RGBA"), overlay)

# Draw elements
draw = ImageDraw.Draw(blurred_bg)

# Song Title
title_font = ImageFont.truetype(FONT_BOLD, 60)
draw.text((50, 50), song_title, font=title_font, fill=(255, 255, 255))

# Artist Name
artist_font = ImageFont.truetype(FONT_REGULAR, 40)
draw.text((50, 130), f"By: {artist_name}", font=artist_font, fill=(200, 200, 200))

# Duration (bottom right)
duration_font = ImageFont.truetype(FONT_BOLD, 35)
draw.text((1100, 650), duration, font=duration_font, fill=(255, 255, 255))

# Progress Bar (Static — Full)
bar_x, bar_y, bar_width, bar_height = 50, 650, 1000, 15
draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill=(100, 100, 100))
draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill=(255, 0, 0))

# Save final thumbnail
blurred_bg.convert("RGB").save(output_path)
print(f"Thumbnail saved as {output_path}")

Example usage

generate_thumbnail( background_url="https://example.com/sample_background.jpg",  # Replace with image URL song_title="Sample Song", artist_name="Sample Artist", duration="03:45", output_path="thumbnail.jpg" )

                   
