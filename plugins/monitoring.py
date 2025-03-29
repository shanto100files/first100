from pyrogram import Client
import asyncio
from datetime import datetime
import logging
from info import LOG_CHANNEL, ADMINS

logger = logging.getLogger(__name__)

async def check_bot_status():
    while True:
        try:
            # চেক বট অনলাইন কিনা
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # চেক সার্ভার রিসোর্স
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            # যদি রিসোর্স বেশি ব্যবহার হয়
            if cpu > 80 or ram > 80:
                alert_msg = f"""
⚠️ **হাই রিসোর্স ইউসেজ অ্যালার্ট!**

CPU: {cpu}%
RAM: {ram}%
Time: {current_time}
                """
                # এডমিনদের অ্যালার্ট করুন
                for admin in ADMINS:
                    try:
                        await Client.send_message(admin, alert_msg)
                    except:
                        pass
                
            # লগ চ্যানেলে স্টেটাস আপডেট
            if LOG_CHANNEL:
                status_msg = f"""
📊 **স্টেটাস আপডেট**
⏰ Time: {current_time}
💻 CPU: {cpu}%
🎮 RAM: {ram}%
                """
                await Client.send_message(LOG_CHANNEL, status_msg)
                
        except Exception as e:
            logger.error(f"মনিটরিং এরর: {str(e)}")
            
        # প্রতি 30 মিনিট পর চেক
        await asyncio.sleep(1800)