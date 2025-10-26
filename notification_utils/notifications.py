# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import time
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import enums
from info import UPDATE_GROUP_ID, UPDATE_NOTIFICATIONS
import logging

# Batching system
BATCH_DELAY = 10  # seconds to wait before sending batch notification
pending_files = []  # List to store pending files for batch notification
batch_timer = None  # Timer for batch processing

logger = logging.getLogger(__name__)

def set_update_group_id(group_id):
    """Set the update group ID from info.py"""
    global UPDATE_GROUP_ID
    UPDATE_GROUP_ID = group_id

async def process_batch_notification(bot: Client):
    """Process and send batch notification for pending files with inline buttons"""
    global pending_files, batch_timer
    
    if not pending_files:
        batch_timer = None
        return
    
    try:
        # Get bot username from temp
        from utils import temp
        bot_username = temp.U_NAME if hasattr(temp, 'U_NAME') and temp.U_NAME else "YourBot"
        
        # Get admin ID from info
        from info import ADMINS
        admin_id = ADMINS[0] if ADMINS else "YourAdmin"
        
        total_files = len(pending_files)
        messages_needed = (total_files + 29) // 30  # 30 files per message (max buttons)
        
        # Send multiple messages if needed
        for msg_num in range(messages_needed):
            start_idx = msg_num * 30
            end_idx = min((msg_num + 1) * 30, total_files)
            current_batch = pending_files[start_idx:end_idx]
            
            # Create message text
            if messages_needed > 1:
                message_text = f"📅 **আজকের আপডেট (Part {msg_num + 1}/{messages_needed})**\n\n"
            else:
                message_text = f"📅 **আজকের আপডেট**\n\n"
            
            # Add file details with global numbering
            for i, file_info in enumerate(current_batch, start_idx + 1):
                file_name = file_info.get('name', 'Unknown')
                file_size = file_info.get('size', 'Unknown')
                message_text += f"📁 **{i}.** `{file_name}`\n"
                message_text += f"📊 **সাইজ:** `{file_size}`\n\n"
        
            message_text += f"🎬 **মুভি/সিরিজ অনলাইন দেখতে ভিজিট করুন:**\n"
            message_text += f"🌐 **Cinemaze.top**\n\n"
            
            message_text += f"📥 **ডাউনলোড করতে ভিজিট করুন:**\n"
            message_text += f"🤖 @{bot_username}\n\n"
            
            message_text += f"⚡ **টেলিগ্রাম ফাইল ছাড়াই ডিরেক্ট লিংক থেকে ডাউনলোড করুন**\n"
            message_text += f"🎯 **দ্রুত ডাউনলোড স্পিড**\n"
            message_text += f"🔒 **নিরাপদ ও সুরক্ষিত**\n"
            message_text += f"📱 **সব ডিভাইসে সাপোর্ট**\n\n"
            
            message_text += f"💎 **প্রিমিয়াম বেনেফিট পেতে যোগাযোগ:**\n"
            message_text += f"👨‍💼 @{admin_id}\n\n"
            
            message_text += f"👇 **নিচের বাটনে ক্লিক করে ফাইল পান**"
            
            # Create inline buttons for current batch
            buttons = []
            for i, file_info in enumerate(current_batch, start_idx + 1):
                file_id = file_info.get('file_id')
                if file_id:
                    # Create button with file number
                    buttons.append(
                        InlineKeyboardButton(
                            f"📥 {i}",
                            callback_data=f"getfile_{file_id}"
                        )
                    )
            
            # Arrange buttons in rows of 6 (fits better)
            button_rows = []
            for i in range(0, len(buttons), 6):
                button_rows.append(buttons[i:i+6])
            
            # Add Get All Files button for this batch
            if len(current_batch) > 1:
                batch_file_ids = ','.join([f['file_id'] for f in current_batch if f.get('file_id')])
                if msg_num == messages_needed - 1 and total_files > 30:
                    # Last message - add button for ALL files
                    all_file_ids = ','.join([f['file_id'] for f in pending_files if f.get('file_id')])
                    button_rows.append([
                        InlineKeyboardButton(
                            f"📦 এই Batch এর সব ({len(current_batch)})",
                            callback_data=f"getallfiles_{batch_file_ids}"
                        ),
                        InlineKeyboardButton(
                            f"📦 সম্পূর্ণ সব ({total_files})",
                            callback_data=f"getallfiles_{all_file_ids}"
                        )
                    ])
                else:
                    button_rows.append([
                        InlineKeyboardButton(
                            f"📦 এই Batch এর সব ({len(current_batch)})",
                            callback_data=f"getallfiles_{batch_file_ids}"
                        )
                    ])
            
            keyboard = InlineKeyboardMarkup(button_rows) if button_rows else None
            
            # Send notification with buttons
            await bot.send_message(
                chat_id=UPDATE_GROUP_ID,
                text=message_text,
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
            
            # Small delay between messages
            if msg_num < messages_needed - 1:
                await asyncio.sleep(1)
        
        logger.info(f"Batch notification sent for {len(pending_files)} files")
        
        # Clear pending files
        pending_files.clear()
        batch_timer = None
        
    except Exception as e:
        logger.error(f"Failed to send batch notification: {e}")
        # Clear pending files even on error to prevent accumulation
        pending_files.clear()
        batch_timer = None

async def send_file_update_notification(bot: Client, file_name: str, file_size: int, file_id: str = None, caption: str = None):
    """
    Add file to batch notification queue instead of sending immediate notification
    
    Args:
        bot: Pyrogram client instance
        file_name: Name of the file
        file_size: Size of the file in bytes
        file_id: Telegram file_id for direct file access
        caption: Optional caption for the file
    """
    global pending_files, batch_timer
    
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
        
        # Add file to pending list
        file_info = {
            'name': file_name,
            'size': size_str,
            'file_id': file_id,
            'caption': caption
        }
        pending_files.append(file_info)
        
        # Cancel existing timer if any
        if batch_timer and not batch_timer.done():
            batch_timer.cancel()
        
        # Start new timer for batch processing
        async def delayed_batch_process():
            await asyncio.sleep(BATCH_DELAY)
            await process_batch_notification(bot)
        
        batch_timer = asyncio.create_task(delayed_batch_process())
        
        logger.info(f"File added to batch queue: {file_name} (Queue size: {len(pending_files)})")
        
    except Exception as e:
        logger.error(f"Failed to add file to batch queue: {e}")

async def send_bulk_update_notification(bot: Client, file_count: int, chat_title: str = None, file_details: list = None):
    """
    Send notification when multiple files are added in bulk
    NOTE: This function is now disabled as individual files use batching system
    
    Args:
        bot: Pyrogram client instance
        file_count: Number of files added
        chat_title: Optional title of the source chat
        file_details: Optional list of file details (name, size)
    """
    
    # Disabled - individual files now use batching system
    logger.info(f"Bulk notification disabled - {file_count} files will be handled by individual batching system")
    return
    
    try:
        # Get bot username from temp
        from utils import temp
        bot_username = temp.U_NAME if hasattr(temp, 'U_NAME') and temp.U_NAME else "YourBot"
        
        # Get admin ID from info
        from info import ADMINS
        admin_id = ADMINS[0] if ADMINS else "YourAdmin"
        
        message_text = f"📅 **আজকের আপডেট**\n\n"
        
        # Add file details if available
        if file_details and len(file_details) > 0:
            for i, file_info in enumerate(file_details[:10], 1):  # Limit to 10 files to avoid message length issues
                file_name = file_info.get('name', 'Unknown')
                file_size = file_info.get('size', 'Unknown')
                message_text += f"📁 **{i}.** `{file_name}`\n"
                message_text += f"📊 **সাইজ:** `{file_size}`\n\n"
            
            if len(file_details) > 10:
                message_text += f"➕ **আরো {len(file_details) - 10} টি ফাইল...**\n\n"
        else:
            message_text += f"📊 **মোট যুক্ত হয়েছে:** `{file_count}` টি নতুন ফাইল\n\n"
        
        if chat_title:
            message_text += f"📂 **সোর্স:** `{chat_title}`\n\n"
        
        message_text += f"🎬 **মুভি/সিরিজ অনলাইন দেখতে ভিজিট করুন:**\n"
        message_text += f"🌐 **Cinemaze.top**\n\n"
        
        message_text += f"📥 **ডাউনলোড করতে ভিজিট করুন:**\n"
        message_text += f"🤖 @{bot_username}\n\n"
        
        message_text += f"⚡ **টেলিগ্রাম ফাইল ছাড়াই ডিরেক্ট লিংক থেকে ডাউনলোড করুন**\n"
        message_text += f"🎯 **দ্রুত ডাউনলোড স্পিড**\n"
        message_text += f"🔒 **নিরাপদ ও সুরক্ষিত**\n"
        message_text += f"📱 **সব ডিভাইসে সাপোর্ট**\n\n"
        
        message_text += f"💎 **প্রিমিয়াম বেনেফিট পেতে যোগাযোগ:**\n"
        message_text += f"👨‍💼 @neil_0998"
        
        # Send notification
        await bot.send_message(
            chat_id=UPDATE_GROUP_ID,
            text=message_text,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
        logger.info(f"Bulk update notification sent for {file_count} files")
        
    except Exception as e:
        logger.error(f"Failed to send bulk update notification: {e}")
