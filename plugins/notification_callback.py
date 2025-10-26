# Notification File Callback Handler
# Handle button clicks from notification messages

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import get_file_details
import logging

logger = logging.getLogger(__name__)

@Client.on_callback_query(filters.regex(r"^getfile_"))
async def send_file_from_notification(client: Client, query: CallbackQuery):
    """
    Send file when user clicks on notification button
    """
    try:
        # Extract file_id from callback data
        file_id = query.data.split("_", 1)[1]
        
        # Answer callback query first
        await query.answer("📥 ফাইল পাঠানো হচ্ছে...", show_alert=False)
        
        # Get file details from database
        files = await get_file_details(file_id)
        
        if not files:
            await query.message.reply_text(
                "❌ দুঃখিত! ফাইল খুঁজে পাওয়া যায়নি।\n"
                "সম্ভবত ফাইলটি ডিলিট হয়ে গেছে।"
            )
            return
        
        file_info = files[0]
        
        # Prepare file caption
        file_name = file_info.get('file_name', 'Unknown')
        file_size = file_info.get('file_size', 0)
        
        # Format file size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        elif file_size < 1024 * 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
        
        caption = f"📁 **{file_name}**\n\n"
        caption += f"📊 **Size:** {size_str}\n\n"
        caption += f"🎬 Powered by CinePix"
        
        # Send file to user in PM
        try:
            await client.send_cached_media(
                chat_id=query.from_user.id,
                file_id=file_id,
                caption=caption
            )
            
            # Notify success
            await query.message.reply_text(
                f"✅ ফাইল আপনার PM এ পাঠানো হয়েছে!\n"
                f"👤 @{query.from_user.username or query.from_user.first_name}",
                reply_to_message_id=query.message.id
            )
            
        except Exception as send_error:
            # If sending fails (user hasn't started bot), show alert
            await query.answer(
                "⚠️ প্রথমে বট স্টার্ট করুন!\n"
                "Bot এ /start করে তারপর আবার try করুন।",
                show_alert=True
            )
            
            # Send button to start bot
            from utils import temp
            bot_username = temp.U_NAME if hasattr(temp, 'U_NAME') else "YourBot"
            
            start_button = InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 Start Bot", url=f"https://t.me/{bot_username}?start=notification")]
            ])
            
            await query.message.reply_text(
                f"👋 Hi {query.from_user.mention}!\n\n"
                f"ফাইল পেতে প্রথমে বট স্টার্ট করুন:",
                reply_markup=start_button
            )
    
    except Exception as e:
        logger.error(f"Error in notification file callback: {e}")
        await query.answer("❌ একটি error হয়েছে!", show_alert=True)


@Client.on_callback_query(filters.regex(r"^getallfiles_"))
async def send_all_files_from_notification(client: Client, query: CallbackQuery):
    """
    Send all files when user clicks on 'Get All Files' button
    """
    try:
        # Extract file_ids from callback data
        file_ids_str = query.data.split("_", 1)[1]
        file_ids = file_ids_str.split(",")
        
        # Answer callback query
        await query.answer(f"📦 {len(file_ids)}টি ফাইল পাঠানো হচ্ছে...", show_alert=False)
        
        sent_count = 0
        failed_count = 0
        
        # Check if user has started bot
        try:
            # Try sending a test message
            test_msg = await client.send_message(
                chat_id=query.from_user.id,
                text=f"📦 **{len(file_ids)}টি ফাইল পাঠানো হচ্ছে...**\n\n"
                     f"⏳ অনুগ্রহ করে অপেক্ষা করুন..."
            )
        except Exception:
            # User hasn't started bot
            await query.answer(
                "⚠️ প্রথমে বট স্টার্ট করুন!\n"
                "Bot এ /start করে তারপর আবার try করুন।",
                show_alert=True
            )
            
            from utils import temp
            bot_username = temp.U_NAME if hasattr(temp, 'U_NAME') else "YourBot"
            
            start_button = InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 Start Bot", url=f"https://t.me/{bot_username}?start=notification")]
            ])
            
            await query.message.reply_text(
                f"👋 Hi {query.from_user.mention}!\n\n"
                f"সব ফাইল পেতে প্রথমে বট স্টার্ট করুন:",
                reply_markup=start_button
            )
            return
        
        # Send each file
        for file_id in file_ids:
            try:
                # Get file details
                files = await get_file_details(file_id)
                
                if not files:
                    failed_count += 1
                    continue
                
                file_info = files[0]
                file_name = file_info.get('file_name', 'Unknown')
                file_size = file_info.get('file_size', 0)
                
                # Format file size
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                elif file_size < 1024 * 1024 * 1024:
                    size_str = f"{file_size / (1024 * 1024):.1f} MB"
                else:
                    size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
                
                caption = f"📁 **{file_name}**\n\n"
                caption += f"📊 **Size:** {size_str}\n\n"
                caption += f"🎬 Powered by CinePix"
                
                # Send file
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=caption
                )
                
                sent_count += 1
                
                # Small delay to avoid flooding
                import asyncio
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Failed to send file {file_id}: {e}")
                failed_count += 1
                continue
        
        # Update progress message
        await test_msg.edit_text(
            f"✅ **সম্পন্ন!**\n\n"
            f"📥 পাঠানো: {sent_count}টি\n"
            f"❌ ব্যর্থ: {failed_count}টি\n\n"
            f"🎬 Powered by CinePix"
        )
        
        # Notify in group
        await query.message.reply_text(
            f"✅ {sent_count}টি ফাইল পাঠানো হয়েছে!\n"
            f"👤 @{query.from_user.username or query.from_user.first_name}",
            reply_to_message_id=query.message.id
        )
        
    except Exception as e:
        logger.error(f"Error in send all files callback: {e}")
        await query.answer("❌ একটি error হয়েছে!", show_alert=True)
