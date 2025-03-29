from pyrogram import Client, filters
from datetime import datetime
import psutil
import time

@Client.on_message(filters.command('status'))
async def check_status(client, message):
    start_time = time.time()
    
    # বট রেসপন্স টাইম চেক
    ping = await message.reply("চেকিং...")
    response_time = round((time.time() - start_time) * 1000, 3)
    
    # সিস্টেম স্ট্যাটস
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    
    status_text = f"""
🤖 **বট স্টেটাস রিপোর্ট**

⚡️ **রেসপন্স টাইম:** `{response_time}ms`
💻 **CPU ব্যবহার:** `{cpu_usage}%`
🎮 **RAM ব্যবহার:** `{ram_usage}%`
💾 **ডিস্ক ব্যবহার:** `{disk_usage}%`
⏰ **আপটাইম:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
    """
    
    await ping.edit_text(status_text)