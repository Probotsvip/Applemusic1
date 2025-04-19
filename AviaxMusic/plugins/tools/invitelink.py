import os
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from SHUKLAMUSIC import app

# Yaha apni special user ID likho
SPECIAL_USER_ID = 7168729089  # Change this to your required user ID

# Command handler for /givelink command (Only for SPECIAL_USER_ID)
@app.on_message(filters.command("givelink") & filters.user(SPECIAL_USER_ID))
async def give_link_command(client, message):
    try:
        link = await app.export_chat_invite_link(message.chat.id)
        await message.reply_text(f"🔗 Invite Link:\n{link}")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# /link ya /invitelink command (Only for SPECIAL_USER_ID)
@app.on_message(filters.command(["link", "invitelink"]) & filters.user(SPECIAL_USER_ID))
async def link_command_handler(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply("Usage: /link group_id")
        return

    group_id = message.command[1]
    file_name = f"group_info_{group_id}.txt"

    try:
        chat = await client.get_chat(int(group_id))
        invite_link = await client.export_chat_invite_link(chat.id)

        group_data = {
            "id": chat.id,
            "type": str(chat.type),
            "title": chat.title,
            "members_count": chat.members_count,
            "description": chat.description,
            "invite_link": invite_link,
            "is_verified": chat.is_verified,
            "is_restricted": chat.is_restricted,
            "is_creator": chat.is_creator,
            "is_scam": chat.is_scam,
            "is_fake": chat.is_fake,
            "dc_id": chat.dc_id,
            "has_protected_content": chat.has_protected_content,
        }

        with open(file_name, "w", encoding="utf-8") as file:
            for key, value in group_data.items():
                file.write(f"{key}: {value}\n")

        await client.send_document(
            chat_id=message.chat.id,
            document=file_name,
            caption=f"🔹 **Group:** {chat.title}\n🔗 **Invite:** {invite_link}",
        )

    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
