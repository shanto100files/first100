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
        # Premium user - show streaming buttons
        download_link = f"{URL}download/{file_id}"
        stream_link = f"{URL}stream/{file_id}"
        
        buttons = [[
            InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download_link),
            InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream_link)
        ],[
            InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream_link))
        ]]
    else:
        # Free user - show only premium button
        buttons = [[
            InlineKeyboardButton("💫 ᴡᴀᴛᴄʜ/ᴅᴏᴡɴʟᴏᴀᴅ 💫", callback_data="stream_limit")
        ]]
    
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

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "stream_limit":
        btn = [
            [InlineKeyboardButton("💫 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ 💫", callback_data="buy_premium")],
            [InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ ⚠️", callback_data="close_data")]
        ]
        
        text = """<b>🔒 Premium Access Required!</b>

<b>This content is only available for Premium users.

Benefits of Premium:
• Unlimited Streaming & Downloads
• Ad-free Experience
• Priority Support
• High Speed Downloads
• All Premium Content Access

Buy Premium now to unlock all features!</b>"""
        
        await query.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex("buy_premium"))
async def buy_premium_handler(client, query):
    btn = [[
        InlineKeyboardButton("💳 বিকাশ পেমেন্ট", callback_data="bkash_payment"),
        InlineKeyboardButton("🏠 হোম", callback_data="start")
    ]]
    
    text = f"""<b>📲 বিকাশ পেমেন্ট প্ল্যান 

💰 উপলব্ধ প্যাকেজ সমূহ:

• ২ সপ্তাহ - ১০ টাকা
• ১ মাস - ২০ টাকা  
• ৩ মাস - ৬০ টাকা
• ৬ মাস - ১২০ টাকা

✅ প্রিমিয়াম ফিচার:
• ভেরিফিকেশন ফ্রি
• সরাসরি ফাইল
• বিজ্ঞাপন মুক্ত
• হাই স্পিড ডাউনলোড
• আনলিমিটেড কন্টেন্ট
• ২৪/৭ সাপোর্ট

বিকাশ নাম্বার: {BKASH_NUMBER}
Send Money করে নিচের বাটনে ক্লিক করুন</b>"""

    await query.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup(btn))


