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

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def truncate(text):
    # Single line truncation like friend's thumbnails
    if len(text) > 28:
        return text[:25] + "..."
    return text

def random_color():
    return (34, 34, 34)  # Fixed dark gray color like friend's

def generate_gradient(width, height, start_color, end_color):
    base = Image.new('RGBA', (width, height), start_color)
    top = Image.new('RGBA', (width, height), end_color)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(60 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def crop_center_circle(img, output_size, border, border_color, crop_scale=1.5):
    half_the_width = img.size[0] / 2
    half_the_height = img.size[1] / 2
    larger_size = int(output_size * crop_scale)
    img = img.crop(
        (
            half_the_width - larger_size/2,
            half_the_height - larger_size/2,
            half_the_width + larger_size/2,
            half_the_height + larger_size/2
        )
    )
    
    img = img.resize((output_size - 2*border, output_size - 2*border))
    
    final_img = Image.new("RGBA", (output_size, output_size), border_color)
    
    mask_main = Image.new("L", (output_size - 2*border, output_size - 2*border), 0)
    draw_main = ImageDraw.Draw(mask_main)
    draw_main.ellipse((0, 0, output_size - 2*border, output_size - 2*border), fill=255)
    
    final_img.paste(img, (border, border), mask_main)
    
    mask_border = Image.new("L", (output_size, output_size), 0)
    draw_border = ImageDraw.Draw(mask_border)
    draw_border.ellipse((0, 0, output_size, output_size), fill=255)
    
    result = Image.composite(final_img, Image.new("RGBA", final_img.size, (0, 0, 0, 0)), mask_border)
    
    return result

def draw_text_with_shadow(background, draw, position, text, font, fill, shadow_offset=(2, 2), shadow_blur=3):
    shadow = Image.new('RGBA', background.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.text(position, text, font=font, fill="black")
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
    background.paste(shadow, shadow_offset, shadow)
    draw.text(position, text, font=font, fill=fill)

async def gen_thumb(videoid: str):
    try:
        if os.path.isfile(f"cache/{videoid}_v4.png"):
            return f"cache/{videoid}_v4.png"

        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = result.get("title")
            if title:
                title = re.sub("\W+", " ", title).title()
            else:
                title = "Unsupported Title"
            duration = result.get("duration")
            if not duration:
                duration = "Live"
            thumbnail_data = result.get("thumbnails")
            if thumbnail_data:
                thumbnail = thumbnail_data[0]["url"].split("?")[0]
            else:
                thumbnail = None
            views_data = result.get("viewCount")
            if views_data:
                views = views_data.get("short") or "Unknown Views"
            else:
                views = "Unknown Views"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/thumb{videoid}.png", mode="wb") as f:
                        await f.write(await resp.read())

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(20))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)

        # Fixed gradient colors like friend's
        gradient_image = generate_gradient(1280, 720, (34, 34, 34), (0, 128, 255))
        background = Image.blend(background, gradient_image, alpha=0.2)
        
        draw = ImageDraw.Draw(background)
        arial = ImageFont.truetype("AviaxMusic/assets/font2.ttf", 28)
        title_font = ImageFont.truetype("AviaxMusic/assets/font3.ttf", 38)

        # Circle thumbnail with friend's style
        circle_thumbnail = crop_center_circle(youtube, 380, 15, (34, 34, 34))
        background.paste(circle_thumbnail, (100, 130), circle_thumbnail)

        # Text positioning like friend's thumbnails
        text_x_position = 500
        title1 = truncate(title)
        draw_text_with_shadow(background, draw, (text_x_position, 150), title1, title_font, (255, 255, 255))
        draw_text_with_shadow(background, draw, (text_x_position, 210), f"YouTube | {views}", arial, (200, 200, 200))

        # Simple progress bar like friend's
        line_length = 580
        draw.line([(text_x_position, 300), (text_x_position + line_length, 300)], fill=(255, 255, 255), width=6)

        # Timestamps
        draw_text_with_shadow(background, draw, (text_x_position, 310), "00:00", arial, (200, 200, 200))
        draw_text_with_shadow(background, draw, (1080, 310), duration, arial, (200, 200, 200))

        os.remove(f"cache/thumb{videoid}.png")
        background_path = f"cache/{videoid}_v4.png"
        background.save(background_path)
        return background_path

    except Exception as e:
        logging.error(f"Error generating thumbnail for video {videoid}: {e}")
        return None
