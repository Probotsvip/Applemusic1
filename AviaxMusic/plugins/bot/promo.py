from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from AviaxMusic import app
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, User
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden, PeerIdInvalid, ChatAdminRequired
from pyrogram.enums import ChatAction, ChatType, MessageEntityType
from pyrogram import Client, filters, enums
from AviaxMusic.misc import SUDOERS

buttons = [
    [
        InlineKeyboardButton(
            text="➕ ᴀᴅᴅ ᴍᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ", 
            url=f"https://t.me/{app.username}?startgroup=s&admin=delete_messages+manage_video_chats+pin_messages+invite_users"
        ),
    ],
]

@app.on_message(filters.command(["promo"]) & SUDOERS)
async def promos(client, message: Message):
    AMBOT = f"""{app.mention},
❖ ɪɴᴛʀᴏᴅᴜᴄɪɴɢ {app.mention}⁩ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ.

🎧 ᴘʟᴀʏ + ᴠᴘʟᴀʏ + ᴄᴘʟᴀʏ 🎧

⦿ 𝖯ʀᴏᴍᴏᴛɪᴏɴ / ᴀᴅs ғʀᴇᴇ ʙᴏᴛ. ✅
⦿ 𝖫ᴀɢ ғʀᴇᴇ 24/7 ʜʀ ᴜᴘᴛɪᴍᴇ. ❤️‍🔥
⦿ 𝖠ᴅᴅ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ. 💌
⦿ 𝖤ɴᴊᴏʏ ɴᴏɴsᴛᴏᴘ ᴍᴜsɪᴄ. 💞

🔐ᴜꜱᴇ » /start ᴛᴏ ᴄʜᴇᴄᴋ ʙᴏᴛ.

➲ ʙᴏᴛ : @Google_music_rebot
"""
    await message.reply(
        text=AMBOT,
        reply_markup=InlineKeyboardMarkup(buttons)
)
