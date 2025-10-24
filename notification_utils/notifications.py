# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import UPDATE_GROUP_ID, UPDATE_NOTIFICATIONS
import logging

logger = logging.getLogger(__name__)

async def send_file_update_notification(bot: Client, file_name: str, file_size: int, caption: str = None):
    """
    Send notification to update group when a new file is added to database
    
    Args:
        bot: Pyrogram client instance
        file_name: Name of the added file
        file_size: Size of the file in bytes
        caption: Optional caption of the file
    """
    
    if not UPDATE_NOTIFICATIONS or not UPDATE_GROUP_ID:
        return
    
    try:
        # Format file size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        elif file_size < 1024 * 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
        
        # Create notification message
        message_text = f"🎬 **নতুন ফাইল যুক্ত হয়েছে!**\n\n"
        message_text += f"📁 **ফাইলের নাম:** `{file_name}`\n"
        message_text += f"📊 **সাইজ:** `{size_str}`\n"
        
        if caption:
            # Clean caption and limit length
            clean_caption = caption.replace('<', '&lt;').replace('>', '&gt;')
            if len(clean_caption) > 200:
                clean_caption = clean_caption[:200] + "..."
            message_text += f"📝 **বিবরণ:** {clean_caption}\n"
        
        message_text += f"\n✅ ফাইলটি সফলভাবে ডাটাবেসে সংরক্ষিত হয়েছে।"
        
        # Send notification (without inline keyboard for channel compatibility)
        await bot.send_message(
            chat_id=UPDATE_GROUP_ID,
            text=message_text,
            parse_mode="md"
        )
        
        logger.info(f"Update notification sent for file: {file_name}")
        
    except Exception as e:
        logger.error(f"Failed to send update notification: {e}")

async def send_bulk_update_notification(bot: Client, file_count: int, chat_title: str = None):
    """
    Send notification when multiple files are added in bulk
    
    Args:
        bot: Pyrogram client instance
        file_count: Number of files added
        chat_title: Optional title of the source chat
    """
    
    if not UPDATE_NOTIFICATIONS or not UPDATE_GROUP_ID or file_count == 0:
        return
    
    try:
        message_text = f"📦 **বাল্ক আপডেট সম্পন্ন!**\n\n"
        message_text += f"📊 **যুক্ত হয়েছে:** `{file_count}` টি নতুন ফাইল\n"
        
        if chat_title:
            message_text += f"📂 **সোর্স:** `{chat_title}`\n"
        
        message_text += f"\n✅ সকল ফাইল সফলভাবে ডাটাবেসে সংরক্ষিত হয়েছে।"
        
        # Send notification
        await bot.send_message(
            chat_id=UPDATE_GROUP_ID,
            text=message_text,
            parse_mode="md"
        )
        
        logger.info(f"Bulk update notification sent for {file_count} files")
        
    except Exception as e:
        logger.error(f"Failed to send bulk update notification: {e}")
