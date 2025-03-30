import asyncio

from pyrogram import filters from pyrogram.enums import ChatMembersFilter from pyrogram.errors import FloodWait

from AviaxMusic import app from AviaxMusic.misc import SUDOERS from AviaxMusic.utils.database import ( get_active_chats, get_authuser_names, get_client, get_served_chats, get_served_users, ) from AviaxMusic.utils.decorators.language import language from AviaxMusic.utils.formatters import alpha_to_int from config import adminlist

IS_BROADCASTING = False

@app.on_message(filters.command("broadcast") & SUDOERS) @language async def broadcast_message(client, message, _): global IS_BROADCASTING

if message.reply_to_message:
    x = message.reply_to_message.id
    y = message.chat.id
else:
    if len(message.command) < 2:
        return await message.reply_text(_["broad_2"])
    query = message.text.split(None, 1)[1]
    if "-pin" in query:
        query = query.replace("-pin", "")
    if "-nobot" in query:
        query = query.replace("-nobot", "")
    if "-pinloud" in query:
        query = query.replace("-pinloud", "")
    if "-assistant" in query:
        query = query.replace("-assistant", "")
    if "-user" in query:
        query = query.replace("-user", "")
    if query == "":
        return await message.reply_text(_["broad_8"])

IS_BROADCASTING = True
await message.reply_text(_["broad_1"])

if "-nobot" not in message.text:
    sent = 0
    pin = 0
    chats = [int(chat["chat_id"]) for chat in await get_served_chats()]
    for i in chats:
        try:
            m = (
                await app.copy_message(i, y, x)
                if message.reply_to_message
                else await app.send_message(i, text=query)
            )
            if "-pin" in message.text:
                try:
                    await m.pin(disable_notification=True)
                    pin += 1
                except:
                    continue
            elif "-pinloud" in message.text:
                try:
                    await m.pin(disable_notification=False)
                    pin += 1
                except:
                    continue
            sent += 1
            await asyncio.sleep(0.2)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except:
            continue
    await message.reply_text(_["broad_3"].format(sent, pin))

if "-user" in message.text:
    sent_users = 0
    users = [int(user["user_id"]) for user in await get_served_users()]
    for i in users:
        try:
            await app.copy_message(i, y, x) if message.reply_to_message else await app.send_message(i, text=query)
            sent_users += 1
            await asyncio.sleep(0.2)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except:
            continue
    await message.reply_text(_["broad_4"].format(sent_users))

if "-assistant" in message.text:
    aw = await message.reply_text(_["broad_5"])
    text = _["broad_6"]
    from AviaxMusic.core.userbot import assistants

    for num in assistants:
        sent = 0
        client = await get_client(num)
        async for dialog in client.get_dialogs():
            try:
                await client.copy_message(dialog.chat.id, y, x) if message.reply_to_message else await client.send_message(dialog.chat.id, text=query)
                sent += 1
                await asyncio.sleep(3)
            except FloodWait as fw:
                await asyncio.sleep(fw.value)
            except:
                continue
        text += _["broad_7"].format(num, sent)
    await aw.edit_text(text)

IS_BROADCASTING = False

async def auto_clean(): while not await asyncio.sleep(10): try: served_chats = await get_active_chats() for chat_id in served_chats: if chat_id not in adminlist: adminlist[chat_id] = [] async for user in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS): if user.privileges.can_manage_video_chats: adminlist[chat_id].append(user.user.id) authusers = await get_authuser_names(chat_id) for user in authusers: user_id = await alpha_to_int(user) adminlist[chat_id].append(user_id) except: continue

asyncio.create_task(auto_clean())

