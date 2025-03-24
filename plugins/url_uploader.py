import os
import aiohttp
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from helper_func.progress_bar import progress_bar
from urllib.parse import urlparse

@Client.on_message(filters.command(["upload", "ul"]) & filters.private)
async def upload_handler(bot: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "**Usage:**\n/upload [url] or /ul [url]\n\n"
            "**Example:**\n/upload https://example.com/file.mp4"
        )
    
    url = message.command[1]
    # URL validation
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return await message.reply_text("❌ Invalid URL")
    except:
        return await message.reply_text("❌ Invalid URL")

    msg = await message.reply_text("📥 Processing URL...")
    
    try:
        # Get file name from URL
        filename = os.path.basename(url)
        if not filename:
            filename = 'downloaded_file'
            
        # Start download
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return await msg.edit("❌ Failed to fetch the file from URL")
                
                # Get file size
                file_size = int(response.headers.get('content-length', 0))
                
                if file_size > 2097152000:  # 2GB limit
                    return await msg.edit("❌ File size is too large (max 2GB)")
                
                # Download and upload
                await msg.edit("📥 Starting Download...")
                
                downloaded = 0
                with open(filename, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024):
                        f.write(chunk)
                        downloaded += len(chunk)
                        await progress_bar(downloaded, file_size, "📥 Downloading...", msg)
                
                await msg.edit("📤 Starting Upload...")
                
                # Upload file
                start_time = time.time()
                try:
                    if filename.lower().endswith(('mp4', 'mkv', 'webm')):
                        await bot.send_video(
                            message.chat.id,
                            video=filename,
                            caption=f"**File Name:** `{filename}`\n**Size:** {humanbytes(file_size)}",
                            progress=progress_bar,
                            progress_args=("📤 Uploading...", msg, start_time)
                        )
                    else:
                        await bot.send_document(
                            message.chat.id,
                            document=filename,
                            caption=f"**File Name:** `{filename}`\n**Size:** {humanbytes(file_size)}",
                            progress=progress_bar,
                            progress_args=("📤 Uploading...", msg, start_time)
                        )
                    
                    await msg.delete()
                    
                except Exception as e:
                    await msg.edit(f"❌ Upload Failed\n\nError: {str(e)}")
                
                finally:
                    try:
                        os.remove(filename)
                    except:
                        pass
                        
    except Exception as e:
        await msg.edit(f"❌ Error: {str(e)}")

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'