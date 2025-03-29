from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery, WebAppInfo
from info import STREAM_MODE, URL, LOG_CHANNEL
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
import humanize
import random
from database.users_chats_db import db

async def check_stream_limit(user_id, file_size):
    # Check if user has premium access
    if await db.has_premium_access(user_id):
        return True
        
    # For free users - 3GB daily limit
    FREE_LIMIT = 3 * 1024 * 1024 * 1024  # 3GB in bytes
    
    current_size = await db.get_daily_download_size(user_id)
    if current_size + file_size > FREE_LIMIT:
        return False
        
    await db.update_daily_download_size(user_id, file_size)
    return True

async def generate_stream_buttons(client, message, file_id, file_size):
    user_id = message.from_user.id
    
    if await db.has_premium_access(user_id):
        # Generate links for all servers
        buttons = []
        for i, base_url in enumerate(STREAM_URLS, 1):
            stream = f"{base_url}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            download = f"{base_url}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            
            buttons.append([
                InlineKeyboardButton(f"• ᴅᴏᴡɴʟᴏᴀᴅ {i} •", url=download),
                InlineKeyboardButton(f'• ᴡᴀᴛᴄʜ {i} •', url=stream)
            ])
        
        buttons.append([
            InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
        ])
        return buttons

    # For free users - check daily limit
    current_size = await db.get_daily_download_size(user_id)
    FREE_LIMIT = 3 * 1024 * 1024 * 1024  # 3GB

    if current_size + file_size > FREE_LIMIT:
        buttons = [[
            InlineKeyboardButton("💫 ᴡᴀᴛᴄʜ/ᴅᴏᴡɴʟᴏᴀᴅ 💫", callback_data="stream_limit")
        ]]
    else:
        # Use first server for free users
        stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        
        buttons = [[
            InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download),
            InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream)
        ],[
            InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
        ]]
        # Update used quota
        await db.update_daily_download_size(user_id, file_size)
    
    return buttons

@Client.on_message(filters.private & filters.command("stream"))
async def stream_start(client, message):
    if STREAM_MODE == False:
        return 
    
    msg = await client.ask(message.chat.id, "**Now send me your file/video to get stream and download link**")
    
    if not msg.media in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.DOCUMENT]:
        return await message.reply("**Please send me supported media.**")
        
    file = getattr(msg, msg.media.value)
    file_size = file.file_size
    
    # Check stream/download limit for free users
    can_stream = await check_stream_limit(message.from_user.id, file_size)
    if not can_stream:
        remaining_gb = (3 - (await db.get_daily_download_size(message.from_user.id))/(1024*1024*1024))
        text = f"""<b>Daily stream/download limit exceeded!</b>
        
• Free users can stream/download up to 3GB per day
• Your remaining quota: {remaining_gb:.2f}GB
• Buy premium for unlimited streaming/downloading
• You can still download directly from bot without limits

Send /plan to see premium plans"""
        return await message.reply_text(text)

    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size) 
    fileid = file.file_id
    user_id = message.from_user.id
    username =  message.from_user.mention 

    log_msg = await client.send_cached_media(
        chat_id=LOG_CHANNEL,
        file_id=fileid,
    )
    fileName = {quote_plus(get_name(log_msg))}
    stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
    download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
 
    await log_msg.reply_text(
        text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
        quote=True,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("🚀 Fast Download 🚀", url=download),  # web download Link
                InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)   # web stream Link
            ]]
        )
    )
    buttons = await generate_stream_buttons(client, message, file.file_id, file.file_size)
    await message.reply_text(
        text=f"**Here is your link!\n\n📁 File: {filename}\n📦 Size: {filesize}**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )




