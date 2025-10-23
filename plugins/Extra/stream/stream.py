from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery, WebAppInfo
from info import STREAM_MODE, URL, LOG_CHANNEL, VERIFY, VERIFY_TUTORIAL
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
import humanize
import random
from database.users_chats_db import db
from utils import check_verification, get_token
import temp

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

async def generate_stream_buttons(client, message, file_id, file_size, download_link=None, stream_link=None):
    user_id = message.from_user.id

    if await db.has_premium_access(user_id):
        # Premium user - show all buttons
        if download_link and stream_link:
            buttons = [[
                InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download_link),
                InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream_link)
            ],[
                InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream_link))
            ]]
            return buttons

    # Check token verification for stream/download access (non-premium users)
    if not await check_verification(client, user_id) and VERIFY == True:
        buttons = [[
            InlineKeyboardButton("🔐 ᴠᴇʀɪꜰʏ ғᴏʀ sᴛʀᴇᴀᴍ/ᴅᴏᴡɴʟᴏᴀᴅ", url=await get_token(client, user_id, f"https://telegram.me/{temp.U_NAME}?start="))
        ]]
        return buttons

    # Free user - check daily limit
    current_size = await db.get_daily_download_size(user_id)
    FREE_LIMIT = 3 * 1024 * 1024 * 1024  # 3GB
    
    if current_size + file_size > FREE_LIMIT:
        # Show premium upgrade button
        buttons = [[
            InlineKeyboardButton("💎 ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ", callback_data="premium_info")
        ]]
        return buttons
    
    # Free user within limit - show stream/download buttons
    if download_link and stream_link:
        buttons = [[
            InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download_link),
            InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream_link)
        ]]
        return buttons
    
    # Default fallback
    return [[InlineKeyboardButton("❌ ᴇʀʀᴏʀ", callback_data="error")]]

@Client.on_message(filters.private & filters.command("stream"))
async def stream_start(client, message):
    if STREAM_MODE == False:
        return

    # Check token verification for stream/download access (except premium users)
    if not await db.has_premium_access(message.from_user.id):
        if not await check_verification(client, message.from_user.id) and VERIFY == True:
            btn = [[
                InlineKeyboardButton("🔐 ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ғᴏʀ sᴛʀᴇᴀᴍ", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start="))
            ],[
                InlineKeyboardButton("ʜᴏᴡ ᴛᴏ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ", url=VERIFY_TUTORIAL)
            ]]
            text = "<b>🔒 sᴛʀᴇᴀᴍ & ᴅᴏᴡɴʟᴏᴀᴅ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʀᴇǫᴜɪʀᴇᴅ!\n\nʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪꜰʏ ʏᴏᴜʀsᴇʟꜰ ᴛᴏ ᴀᴄᴄᴇss sᴛʀᴇᴀᴍ & ᴅᴏᴡɴʟᴏᴀᴅ ғᴇᴀᴛᴜʀᴇs.\n\n⏰ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴠᴀʟɪᴅ ғᴏʀ 12 ʜᴏᴜʀs\n\n💡 ɴᴏᴛᴇ: ᴅɪʀᴇᴄᴛ ғɪʟᴇ ᴀᴄᴄᴇss ɪs sᴛɪʟʟ ғʀᴇᴇ!</b>"
            await message.reply_text(
                text=text,
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(btn)
            )
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
    fileName = quote_plus(get_name(log_msg))
    file_id = str(log_msg.id)
    file_hash = get_hash(log_msg)

    # Create permanent links that won't change
    permanent_id = f"{file_hash}{file_id}" # Combine hash and ID for stability

    # Regular links (may change)
    stream = f"{URL}watch/{file_id}/{fileName}?hash={file_hash}"
    download = f"{URL}{file_id}/{fileName}?hash={file_hash}"

    # Permanent links (won't change)
    # Version with hash (more secure)
    permanent_stream_with_hash = f"{URL}p/{permanent_id}/{fileName}?hash={file_hash}"
    permanent_download_with_hash = f"{URL}p/{permanent_id}/{fileName}?hash={file_hash}"

    # Version without hash (simpler to use)
    permanent_stream = f"{URL}p/{permanent_id}/{fileName}"
    permanent_download = f"{URL}p/{permanent_id}/{fileName}"

    await log_msg.reply_text(
        text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᗴ : {fileName}",
        quote=True,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("🚀 Fast Download 🚀", url=download),  # web download Link
                InlineKeyboardButton('🖥️ Watch online 🖥️', url=stream)   # web stream Link
            ],[
                InlineKeyboardButton("♾️ Permanent Download ♾️", url=permanent_download),  # permanent download Link
                InlineKeyboardButton('♾️ Permanent Stream ♾️', url=permanent_stream)   # permanent stream Link
            ]]
        )
    )
    # Create buttons with permanent links
    buttons = [
        [
            InlineKeyboardButton("🚀 Download 🚀", url=download),
            InlineKeyboardButton('🖥️ Stream 🖥️', url=stream)
        ],
        [
            InlineKeyboardButton("♾️ Permanent Download ♾️", url=permanent_download),
            InlineKeyboardButton('♾️ Permanent Stream ♾️', url=permanent_stream)
        ]
    ]

    await message.reply_text(
        text=f"**Here is your link!\n\n📁 File: {filename}\n📦 Size: {filesize}\n\n❗️ Use Permanent links for long-term access**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


