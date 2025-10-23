# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from database.users_chats_db import db
from info import ADMINS
from utils import get_seconds

# Premium User Management Commands for Admins

@Client.on_message(filters.command("premium_users") & filters.user(ADMINS))
async def premium_users_list(client, message):
    """Show list of all premium users"""
    try:
        premium_users = await db.get_all_premium_users()
        
        if not premium_users:
            await message.reply("📭 **কোন প্রিমিয়াম ইউজার নেই।**")
            return
        
        text = "👑 **প্রিমিয়াম ইউজারদের তালিকা:**\n\n"
        
        for i, user in enumerate(premium_users[:20], 1):  # Show first 20 users
            user_id = user['user_id']
            expiry = user['expiry_time']
            remaining = expiry - datetime.datetime.now()
            days_left = remaining.days
            
            # Get user info from Telegram
            try:
                user_info = await client.get_users(user_id)
                name = user_info.first_name
                username = f"@{user_info.username}" if user_info.username else "No Username"
            except:
                name = "Unknown"
                username = "N/A"
            
            text += f"**{i}.** `{user_id}` - **{name}**\n"
            text += f"   └ Username: {username}\n"
            text += f"   └ মেয়াদ: **{days_left} দিন** বাকি\n"
            text += f"   └ শেষ হবে: `{expiry.strftime('%d/%m/%Y %H:%M')}`\n\n"
        
        if len(premium_users) > 20:
            text += f"**... আরও {len(premium_users) - 20}টি ইউজার আছে**\n\n"
        
        # Add navigation buttons
        buttons = [
            [InlineKeyboardButton("📊 পরিসংখ্যান", callback_data="premium_stats")],
            [InlineKeyboardButton("🔍 খুঁজুন", callback_data="premium_search"),
             InlineKeyboardButton("➕ যোগ করুন", callback_data="add_premium")],
            [InlineKeyboardButton("❌ বন্ধ করুন", callback_data="close_data")]
        ]
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
        
    except Exception as e:
        await message.reply(f"❌ **এরর:** `{str(e)}`")

@Client.on_message(filters.command("premium_stats") & filters.user(ADMINS))
async def premium_statistics(client, message):
    """Show premium user statistics"""
    try:
        stats = await db.get_premium_stats()
        
        text = f"""📊 **প্রিমিয়াম ইউজার পরিসংখ্যান:**

👑 **সক্রিয় প্রিমিয়াম:** `{stats['total_premium']}` জন
⏰ **মেয়াদ শেষ:** `{stats['expired_premium']}` জন  
🆓 **ফ্রি ট্রায়াল:** `{stats['free_trial_users']}` জন
⚠️ **৭ দিনে শেষ:** `{stats['expiring_soon']}` জন

📈 **মোট ইউজার:** `{stats['total_premium'] + stats['expired_premium']}` জন"""

        buttons = [
            [InlineKeyboardButton("👑 প্রিমিয়াম তালিকা", callback_data="premium_list")],
            [InlineKeyboardButton("⚠️ শীঘ্রই শেষ", callback_data="expiring_users")],
            [InlineKeyboardButton("❌ বন্ধ করুন", callback_data="close_data")]
        ]
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
        
    except Exception as e:
        await message.reply(f"❌ **এরর:** `{str(e)}`")

@Client.on_message(filters.command("add_premium") & filters.user(ADMINS))
async def add_premium_user(client, message):
    """Add premium access to a user"""
    try:
        if len(message.command) < 3:
            await message.reply(
                "📝 **ব্যবহার:**\n"
                "`/add_premium <user_id> <days>`\n\n"
                "**উদাহরণ:**\n"
                "`/add_premium 123456789 30`"
            )
            return
        
        user_id = int(message.command[1])
        days = int(message.command[2])
        
        if days <= 0:
            await message.reply("❌ **দিনের সংখ্যা ০ এর চেয়ে বেশি হতে হবে।**")
            return
        
        # Add premium access
        expiry_time = await db.add_premium_user(user_id, days)
        
        # Get user info
        try:
            user_info = await client.get_users(user_id)
            name = user_info.first_name
            username = f"@{user_info.username}" if user_info.username else "No Username"
        except:
            name = "Unknown User"
            username = "N/A"
        
        text = f"""✅ **প্রিমিয়াম অ্যাক্সেস যোগ করা হয়েছে!**

👤 **ইউজার:** `{user_id}` - **{name}**
📱 **Username:** {username}
⏰ **মেয়াদ:** **{days} দিন**
📅 **শেষ হবে:** `{expiry_time.strftime('%d/%m/%Y %H:%M')}`

🎉 **ইউজারটি এখন প্রিমিয়াম সুবিধা পাবে!**"""
        
        await message.reply(text)
        
        # Notify the user
        try:
            await client.send_message(
                user_id,
                f"🎉 **অভিনন্দন!**\n\n"
                f"আপনাকে **{days} দিনের** প্রিমিয়াম অ্যাক্সেস দেওয়া হয়েছে!\n"
                f"মেয়াদ শেষ: `{expiry_time.strftime('%d/%m/%Y %H:%M')}`\n\n"
                f"💎 **প্রিমিয়াম সুবিধা:**\n"
                f"• আনলিমিটেড ডাউনলোড\n"
                f"• দ্রুত স্পিড\n"
                f"• বিজ্ঞাপন মুক্ত\n"
                f"• প্রাইওরিটি সাপোর্ট"
            )
        except:
            pass
        
    except ValueError:
        await message.reply("❌ **ভুল ফরম্যাট। সংখ্যা ব্যবহার করুন।**")
    except Exception as e:
        await message.reply(f"❌ **এরর:** `{str(e)}`")

@Client.on_message(filters.command("remove_premium") & filters.user(ADMINS))
async def remove_premium_user(client, message):
    """Remove premium access from a user"""
    try:
        if len(message.command) < 2:
            await message.reply(
                "📝 **ব্যবহার:**\n"
                "`/remove_premium <user_id>`\n\n"
                "**উদাহরণ:**\n"
                "`/remove_premium 123456789`"
            )
            return
        
        user_id = int(message.command[1])
        
        # Check if user has premium
        if not await db.has_premium_access(user_id):
            await message.reply("❌ **এই ইউজারের কোন প্রিমিয়াম অ্যাক্সেস নেই।**")
            return
        
        # Remove premium access
        await db.remove_premium_user(user_id)
        
        # Get user info
        try:
            user_info = await client.get_users(user_id)
            name = user_info.first_name
            username = f"@{user_info.username}" if user_info.username else "No Username"
        except:
            name = "Unknown User"
            username = "N/A"
        
        text = f"""✅ **প্রিমিয়াম অ্যাক্সেস সরানো হয়েছে!**

👤 **ইউজার:** `{user_id}` - **{name}**
📱 **Username:** {username}

⚠️ **ইউজারটি এখন ফ্রি ইউজার হয়ে গেছে।**"""
        
        await message.reply(text)
        
        # Notify the user
        try:
            await client.send_message(
                user_id,
                "⚠️ **প্রিমিয়াম মেয়াদ শেষ**\n\n"
                "আপনার প্রিমিয়াম অ্যাক্সেস সরিয়ে দেওয়া হয়েছে।\n"
                "এখন আপনি ফ্রি ইউজার হিসেবে সীমিত সুবিধা পাবেন।\n\n"
                "নতুন প্রিমিয়াম প্ল্যানের জন্য /plan কমান্ড ব্যবহার করুন।"
            )
        except:
            pass
        
    except ValueError:
        await message.reply("❌ **ভুল ফরম্যাট। সংখ্যা ব্যবহার করুন।**")
    except Exception as e:
        await message.reply(f"❌ **এরর:** `{str(e)}`")

@Client.on_message(filters.command("extend_premium") & filters.user(ADMINS))
async def extend_premium_user(client, message):
    """Extend premium access for a user"""
    try:
        if len(message.command) < 3:
            await message.reply(
                "📝 **ব্যবহার:**\n"
                "`/extend_premium <user_id> <additional_days>`\n\n"
                "**উদাহরণ:**\n"
                "`/extend_premium 123456789 15`"
            )
            return
        
        user_id = int(message.command[1])
        additional_days = int(message.command[2])
        
        if additional_days <= 0:
            await message.reply("❌ **দিনের সংখ্যা ০ এর চেয়ে বেশি হতে হবে।**")
            return
        
        # Extend premium access
        new_expiry = await db.extend_premium_user(user_id, additional_days)
        
        if not new_expiry:
            await message.reply("❌ **ইউজার খুঁজে পাওয়া যায়নি।**")
            return
        
        # Get user info
        try:
            user_info = await client.get_users(user_id)
            name = user_info.first_name
            username = f"@{user_info.username}" if user_info.username else "No Username"
        except:
            name = "Unknown User"
            username = "N/A"
        
        text = f"""✅ **প্রিমিয়াম মেয়াদ বাড়ানো হয়েছে!**

👤 **ইউজার:** `{user_id}` - **{name}**
📱 **Username:** {username}
➕ **অতিরিক্ত:** **{additional_days} দিন**
📅 **নতুন মেয়াদ:** `{new_expiry.strftime('%d/%m/%Y %H:%M')}`

🎉 **ইউজারের প্রিমিয়াম মেয়াদ বৃদ্ধি পেয়েছে!**"""
        
        await message.reply(text)
        
        # Notify the user
        try:
            await client.send_message(
                user_id,
                f"🎉 **প্রিমিয়াম মেয়াদ বৃদ্ধি!**\n\n"
                f"আপনার প্রিমিয়াম মেয়াদ **{additional_days} দিন** বাড়ানো হয়েছে!\n"
                f"নতুন মেয়াদ শেষ: `{new_expiry.strftime('%d/%m/%Y %H:%M')}`\n\n"
                f"💎 **প্রিমিয়াম সুবিধা চালু থাকবে!**"
            )
        except:
            pass
        
    except ValueError:
        await message.reply("❌ **ভুল ফরম্যাট। সংখ্যা ব্যবহার করুন।**")
    except Exception as e:
        await message.reply(f"❌ **এরর:** `{str(e)}`")

@Client.on_message(filters.command("premium_info") & filters.user(ADMINS))
async def premium_user_info(client, message):
    """Get detailed info about a premium user"""
    try:
        if len(message.command) < 2:
            await message.reply(
                "📝 **ব্যবহার:**\n"
                "`/premium_info <user_id>`\n\n"
                "**উদাহরণ:**\n"
                "`/premium_info 123456789`"
            )
            return
        
        user_id = int(message.command[1])
        
        # Get premium user details
        details = await db.get_premium_user_details(user_id)
        
        if not details:
            await message.reply("❌ **এই ইউজারের কোন প্রিমিয়াম অ্যাক্সেস নেই।**")
            return
        
        # Get user info from Telegram
        try:
            user_info = await client.get_users(user_id)
            name = user_info.first_name
            username = f"@{user_info.username}" if user_info.username else "No Username"
        except:
            name = "Unknown User"
            username = "N/A"
        
        remaining = details['remaining_time']
        days_left = remaining.days
        hours_left = remaining.seconds // 3600
        
        text = f"""👤 **প্রিমিয়াম ইউজারের তথ্য:**

**📋 ব্যক্তিগত তথ্য:**
• **নাম:** {name}
• **ইউজার ID:** `{user_id}`
• **Username:** {username}

**💎 প্রিমিয়াম তথ্য:**
• **মেয়াদ শেষ:** `{details['expiry_time'].strftime('%d/%m/%Y %H:%M')}`
• **বাকি সময়:** **{days_left} দিন {hours_left} ঘন্টা**
• **ফ্রি ট্রায়াল:** {'✅ হ্যাঁ' if details['has_free_trial'] else '❌ না'}

**📊 ব্যবহারের তথ্য:**
• **আজকের রিকুয়েস্ট:** `{details['daily_requests']}`
• **মোট রিকুয়েস্ট:** `{details['total_requests']}`
• **দৈনিক সীমা:** `{details['max_daily_requests']}`"""

        buttons = [
            [InlineKeyboardButton("➕ মেয়াদ বাড়ান", callback_data=f"extend_user_{user_id}"),
             InlineKeyboardButton("❌ সরান", callback_data=f"remove_user_{user_id}")],
            [InlineKeyboardButton("🔄 রিফ্রেশ", callback_data=f"refresh_info_{user_id}"),
             InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
        ]
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
        
    except ValueError:
        await message.reply("❌ **ভুল ফরম্যাট। সংখ্যা ব্যবহার করুন।**")
    except Exception as e:
        await message.reply(f"❌ **এরর:** `{str(e)}`")

# Callback Query Handlers
@Client.on_callback_query(filters.regex("premium_"))
async def premium_callback_handler(client, query: CallbackQuery):
    """Handle premium management callbacks"""
    if query.from_user.id not in ADMINS:
        await query.answer("❌ আপনার এই কমান্ড ব্যবহারের অনুমতি নেই!", show_alert=True)
        return
    
    data = query.data
    
    if data == "premium_stats":
        try:
            stats = await db.get_premium_stats()
            
            text = f"""📊 **প্রিমিয়াম ইউজার পরিসংখ্যান:**

👑 **সক্রিয় প্রিমিয়াম:** `{stats['total_premium']}` জন
⏰ **মেয়াদ শেষ:** `{stats['expired_premium']}` জন  
🆓 **ফ্রি ট্রায়াল:** `{stats['free_trial_users']}` জন
⚠️ **৭ দিনে শেষ:** `{stats['expiring_soon']}` জন

📈 **মোট ইউজার:** `{stats['total_premium'] + stats['expired_premium']}` জন"""

            buttons = [
                [InlineKeyboardButton("👑 প্রিমিয়াম তালিকা", callback_data="premium_list")],
                [InlineKeyboardButton("⚠️ শীঘ্রই শেষ", callback_data="expiring_users")],
                [InlineKeyboardButton("🔙 ফিরে যান", callback_data="premium_main"),
                 InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
            ]
            
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
            
        except Exception as e:
            await query.answer(f"❌ এরর: {str(e)}", show_alert=True)
    
    elif data == "premium_list":
        try:
            premium_users = await db.get_all_premium_users()
            
            if not premium_users:
                await query.answer("📭 কোন প্রিমিয়াম ইউজার নেই।", show_alert=True)
                return
            
            text = "👑 **প্রিমিয়াম ইউজারদের তালিকা:**\n\n"
            
            for i, user in enumerate(premium_users[:10], 1):  # Show first 10 users
                user_id = user['user_id']
                expiry = user['expiry_time']
                remaining = expiry - datetime.datetime.now()
                days_left = remaining.days
                
                try:
                    user_info = await client.get_users(user_id)
                    name = user_info.first_name[:15] + "..." if len(user_info.first_name) > 15 else user_info.first_name
                except:
                    name = "Unknown"
                
                text += f"**{i}.** `{user_id}` - **{name}**\n"
                text += f"   └ **{days_left} দিন** বাকি\n\n"
            
            if len(premium_users) > 10:
                text += f"**... আরও {len(premium_users) - 10}টি ইউজার**\n\n"
            
            buttons = [
                [InlineKeyboardButton("📊 পরিসংখ্যান", callback_data="premium_stats")],
                [InlineKeyboardButton("🔙 ফিরে যান", callback_data="premium_main"),
                 InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
            ]
            
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
            
        except Exception as e:
            await query.answer(f"❌ এরর: {str(e)}", show_alert=True)
    
    elif data == "expiring_users":
        try:
            # Get users expiring in next 7 days
            next_week = datetime.datetime.now() + datetime.timedelta(days=7)
            expiring_users = await db.search_premium_users(status="active")
            
            # Filter users expiring in next 7 days
            expiring_soon = []
            for user_data in expiring_users:
                expiry = user_data.get('expiry_time')
                if expiry and expiry < next_week:
                    expiring_soon.append(user_data)
            
            if not expiring_soon:
                await query.answer("✅ কোন ইউজারের মেয়াদ শীঘ্রই শেষ হচ্ছে না।", show_alert=True)
                return
            
            text = "⚠️ **শীঘ্রই মেয়াদ শেষ হবে:**\n\n"
            
            for i, user_data in enumerate(expiring_soon[:10], 1):
                user_id = user_data['id']
                expiry = user_data['expiry_time']
                remaining = expiry - datetime.datetime.now()
                days_left = remaining.days
                
                try:
                    user_info = await client.get_users(user_id)
                    name = user_info.first_name[:15] + "..." if len(user_info.first_name) > 15 else user_info.first_name
                except:
                    name = "Unknown"
                
                text += f"**{i}.** `{user_id}` - **{name}**\n"
                text += f"   └ **{days_left} দিন** বাকি\n\n"
            
            buttons = [
                [InlineKeyboardButton("📊 পরিসংখ্যান", callback_data="premium_stats")],
                [InlineKeyboardButton("🔙 ফিরে যান", callback_data="premium_main"),
                 InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
            ]
            
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
            
        except Exception as e:
            await query.answer(f"❌ এরর: {str(e)}", show_alert=True)

@Client.on_message(filters.command("search_premium") & filters.user(ADMINS))
async def search_premium_users(client, message):
    """Search premium users by user ID or username"""
    try:
        if len(message.command) < 2:
            await message.reply(
                "🔍 **প্রিমিয়াম ইউজার খুঁজুন:**\n\n"
                "📝 **ব্যবহার:**\n"
                "`/search_premium <user_id/username>`\n\n"
                "**উদাহরণ:**\n"
                "`/search_premium 123456789`\n"
                "`/search_premium @username`"
            )
            return
        
        search_term = message.command[1]
        
        # Remove @ if present in username
        if search_term.startswith('@'):
            search_term = search_term[1:]
        
        # Try to get user info first
        try:
            if search_term.isdigit():
                user_id = int(search_term)
                user_info = await client.get_users(user_id)
            else:
                user_info = await client.get_users(search_term)
                user_id = user_info.id
        except:
            await message.reply("❌ **ইউজার খুঁজে পাওয়া যায়নি।**")
            return
        
        # Check if user has premium
        details = await db.get_premium_user_details(user_id)
        
        if not details:
            await message.reply(
                f"❌ **ইউজার পাওয়া গেছে কিন্তু প্রিমিয়াম নয়:**\n\n"
                f"👤 **নাম:** {user_info.first_name}\n"
                f"📱 **Username:** @{user_info.username if user_info.username else 'N/A'}\n"
                f"🆔 **ID:** `{user_id}`\n\n"
                f"💡 **প্রিমিয়াম দিতে:** `/add_premium {user_id} <days>`"
            )
            return
        
        # Show premium user details
        name = user_info.first_name
        username = f"@{user_info.username}" if user_info.username else "No Username"
        
        remaining = details['remaining_time']
        days_left = remaining.days
        hours_left = remaining.seconds // 3600
        
        text = f"""✅ **প্রিমিয়াম ইউজার পাওয়া গেছে:**

**📋 ব্যক্তিগত তথ্য:**
• **নাম:** {name}
• **ইউজার ID:** `{user_id}`
• **Username:** {username}

**💎 প্রিমিয়াম তথ্য:**
• **মেয়াদ শেষ:** `{details['expiry_time'].strftime('%d/%m/%Y %H:%M')}`
• **বাকি সময়:** **{days_left} দিন {hours_left} ঘন্টা**
• **ফ্রি ট্রায়াল:** {'✅ হ্যাঁ' if details['has_free_trial'] else '❌ না'}

**📊 ব্যবহারের তথ্য:**
• **আজকের রিকুয়েস্ট:** `{details['daily_requests']}`
• **মোট রিকুয়েস্ট:** `{details['total_requests']}`
• **দৈনিক সীমা:** `{details['max_daily_requests']}`"""

        buttons = [
            [InlineKeyboardButton("➕ মেয়াদ বাড়ান", callback_data=f"extend_user_{user_id}"),
             InlineKeyboardButton("❌ সরান", callback_data=f"remove_user_{user_id}")],
            [InlineKeyboardButton("📊 পরিসংখ্যান", callback_data="premium_stats"),
             InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
        ]
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
        
    except Exception as e:
        await message.reply(f"❌ **এরর:** `{str(e)}`")

@Client.on_message(filters.command("filter_premium") & filters.user(ADMINS))
async def filter_premium_users(client, message):
    """Filter premium users by different criteria"""
    try:
        if len(message.command) < 2:
            await message.reply(
                "🔍 **প্রিমিয়াম ইউজার ফিল্টার:**\n\n"
                "📝 **ব্যবহার:**\n"
                "`/filter_premium <filter_type>`\n\n"
                "**ফিল্টার অপশন:**\n"
                "• `active` - সক্রিয় প্রিমিয়াম ইউজার\n"
                "• `expired` - মেয়াদ শেষ ইউজার\n"
                "• `expiring` - ৭ দিনে শেষ হবে\n"
                "• `trial` - ফ্রি ট্রায়াল ইউজার\n"
                "• `new` - নতুন প্রিমিয়াম (৭ দিনের মধ্যে)\n\n"
                "**উদাহরণ:**\n"
                "`/filter_premium active`"
            )
            return
        
        filter_type = message.command[1].lower()
        
        if filter_type == "active":
            users = await db.search_premium_users(status="active")
            title = "🟢 **সক্রিয় প্রিমিয়াম ইউজার**"
        elif filter_type == "expired":
            users = await db.search_premium_users(status="expired")
            title = "🔴 **মেয়াদ শেষ প্রিমিয়াম ইউজার**"
        elif filter_type == "expiring":
            users = await db.search_premium_users(status="expiring")
            title = "⚠️ **শীঘ্রই মেয়াদ শেষ (৭ দিন)**"
        elif filter_type == "trial":
            users = await db.search_premium_users(has_trial=True)
            title = "🆓 **ফ্রি ট্রায়াল ইউজার**"
        elif filter_type == "new":
            users = await db.search_premium_users(status="new")
            title = "🆕 **নতুন প্রিমিয়াম ইউজার (৭ দিন)**"
        else:
            await message.reply(
                "❌ **ভুল ফিল্টার টাইপ।**\n\n"
                "**সঠিক অপশন:** `active`, `expired`, `expiring`, `trial`, `new`"
            )
            return
        
        if not users:
            await message.reply(f"📭 **{title} এর অধীনে কোন ইউজার নেই।**")
            return
        
        text = f"{title}\n\n"
        
        for i, user_data in enumerate(users[:15], 1):  # Show first 15 users
            user_id = user_data.get('id') or user_data.get('user_id')
            
            try:
                user_info = await client.get_users(user_id)
                name = user_info.first_name[:12] + "..." if len(user_info.first_name) > 12 else user_info.first_name
                username = f"@{user_info.username}" if user_info.username else "N/A"
            except:
                name = "Unknown"
                username = "N/A"
            
            if filter_type in ["active", "expiring", "new"]:
                expiry = user_data.get('expiry_time')
                if expiry:
                    remaining = expiry - datetime.datetime.now()
                    days_left = remaining.days
                    text += f"**{i}.** `{user_id}` - **{name}**\n"
                    text += f"   └ Username: {username}\n"
                    text += f"   └ **{days_left} দিন** বাকি\n\n"
                else:
                    text += f"**{i}.** `{user_id}` - **{name}**\n"
                    text += f"   └ Username: {username}\n\n"
            else:
                text += f"**{i}.** `{user_id}` - **{name}**\n"
                text += f"   └ Username: {username}\n\n"
        
        if len(users) > 15:
            text += f"**... আরও {len(users) - 15}টি ইউজার আছে**\n\n"
        
        text += f"**মোট:** `{len(users)}` জন"
        
        buttons = [
            [InlineKeyboardButton("📊 পরিসংখ্যান", callback_data="premium_stats")],
            [InlineKeyboardButton("👑 সব প্রিমিয়াম", callback_data="premium_list"),
             InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
        ]
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
        
    except Exception as e:
        await message.reply(f"❌ **এরর:** `{str(e)}`")

@Client.on_message(filters.command("premium_help") & filters.user(ADMINS))
async def premium_help(client, message):
    """Show help for premium management commands"""
    text = """🔧 **প্রিমিয়াম ম্যানেজমেন্ট কমান্ড:**

**📋 তালিকা ও তথ্য:**
• `/premium_users` - সব প্রিমিয়াম ইউজার দেখুন
• `/premium_stats` - পরিসংখ্যান দেখুন
• `/premium_info <user_id>` - নির্দিষ্ট ইউজারের তথ্য

**➕ যোগ ও সরানো:**
• `/add_premium <user_id> <days>` - প্রিমিয়াম দিন
• `/remove_premium <user_id>` - প্রিমিয়াম সরান
• `/extend_premium <user_id> <days>` - মেয়াদ বাড়ান

**🔍 খোঁজা ও ফিল্টার:**
• `/search_premium <user_id/username>` - ইউজার খুঁজুন
• `/filter_premium <type>` - ফিল্টার করুন

**ফিল্টার অপশন:**
• `active` - সক্রিয় প্রিমিয়াম
• `expired` - মেয়াদ শেষ
• `expiring` - ৭ দিনে শেষ
• `trial` - ফ্রি ট্রায়াল
• `new` - নতুন প্রিমিয়াম

**💡 উদাহরণ:**
• `/add_premium 123456789 30`
• `/search_premium @username`
• `/filter_premium active`"""

    buttons = [
        [InlineKeyboardButton("📊 পরিসংখ্যান", callback_data="premium_stats")],
        [InlineKeyboardButton("👑 প্রিমিয়াম তালিকা", callback_data="premium_list")],
        [InlineKeyboardButton("❌ বন্ধ করুন", callback_data="close_data")]
    ]
    
    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))

# Additional callback handlers for user actions
@Client.on_callback_query(filters.regex(r"extend_user_(\d+)"))
async def extend_user_callback(client, query: CallbackQuery):
    """Handle extend user callback"""
    if query.from_user.id not in ADMINS:
        await query.answer("❌ আপনার এই কমান্ড ব্যবহারের অনুমতি নেই!", show_alert=True)
        return
    
    user_id = int(query.data.split("_")[2])
    
    text = f"""➕ **প্রিমিয়াম মেয়াদ বাড়ান:**

👤 **ইউজার ID:** `{user_id}`

📝 **কমান্ড ব্যবহার করুন:**
`/extend_premium {user_id} <days>`

**উদাহরণ:**
`/extend_premium {user_id} 15`"""

    buttons = [
        [InlineKeyboardButton("🔙 ফিরে যান", callback_data=f"refresh_info_{user_id}"),
         InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"remove_user_(\d+)"))
async def remove_user_callback(client, query: CallbackQuery):
    """Handle remove user callback"""
    if query.from_user.id not in ADMINS:
        await query.answer("❌ আপনার এই কমান্ড ব্যবহারের অনুমতি নেই!", show_alert=True)
        return
    
    user_id = int(query.data.split("_")[2])
    
    text = f"""❌ **প্রিমিয়াম অ্যাক্সেস সরান:**

👤 **ইউজার ID:** `{user_id}`

⚠️ **সতর্কতা:** এই কাজটি পূর্বাবস্থায় ফেরানো যাবে না।

📝 **কমান্ড ব্যবহার করুন:**
`/remove_premium {user_id}`"""

    buttons = [
        [InlineKeyboardButton("✅ নিশ্চিত করুন", callback_data=f"confirm_remove_{user_id}")],
        [InlineKeyboardButton("🔙 ফিরে যান", callback_data=f"refresh_info_{user_id}"),
         InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"confirm_remove_(\d+)"))
async def confirm_remove_callback(client, query: CallbackQuery):
    """Confirm and remove premium user"""
    if query.from_user.id not in ADMINS:
        await query.answer("❌ আপনার এই কমান্ড ব্যবহারের অনুমতি নেই!", show_alert=True)
        return
    
    user_id = int(query.data.split("_")[2])
    
    try:
        # Check if user has premium
        if not await db.has_premium_access(user_id):
            await query.answer("❌ এই ইউজারের কোন প্রিমিয়াম অ্যাক্সেস নেই।", show_alert=True)
            return
        
        # Remove premium access
        await db.remove_premium_user(user_id)
        
        # Get user info
        try:
            user_info = await client.get_users(user_id)
            name = user_info.first_name
        except:
            name = "Unknown User"
        
        text = f"""✅ **প্রিমিয়াম অ্যাক্সেস সরানো হয়েছে!**

👤 **ইউজার:** `{user_id}` - **{name}**

⚠️ **ইউজারটি এখন ফ্রি ইউজার হয়ে গেছে।**"""
        
        buttons = [
            [InlineKeyboardButton("📊 পরিসংখ্যান", callback_data="premium_stats")],
            [InlineKeyboardButton("👑 প্রিমিয়াম তালিকা", callback_data="premium_list")],
            [InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        
        # Notify the user
        try:
            await client.send_message(
                user_id,
                "⚠️ **প্রিমিয়াম মেয়াদ শেষ**\n\n"
                "আপনার প্রিমিয়াম অ্যাক্সেস সরিয়ে দেওয়া হয়েছে।\n"
                "এখন আপনি ফ্রি ইউজার হিসেবে সীমিত সুবিধা পাবেন।\n\n"
                "নতুন প্রিমিয়াম প্ল্যানের জন্য /plan কমান্ড ব্যবহার করুন।"
            )
        except:
            pass
        
    except Exception as e:
        await query.answer(f"❌ এরর: {str(e)}", show_alert=True)

@Client.on_callback_query(filters.regex(r"refresh_info_(\d+)"))
async def refresh_info_callback(client, query: CallbackQuery):
    """Refresh user info"""
    if query.from_user.id not in ADMINS:
        await query.answer("❌ আপনার এই কমান্ড ব্যবহারের অনুমতি নেই!", show_alert=True)
        return
    
    user_id = int(query.data.split("_")[2])
    
    try:
        # Get premium user details
        details = await db.get_premium_user_details(user_id)
        
        if not details:
            await query.answer("❌ এই ইউজারের কোন প্রিমিয়াম অ্যাক্সেস নেই।", show_alert=True)
            return
        
        # Get user info from Telegram
        try:
            user_info = await client.get_users(user_id)
            name = user_info.first_name
            username = f"@{user_info.username}" if user_info.username else "No Username"
        except:
            name = "Unknown User"
            username = "N/A"
        
        remaining = details['remaining_time']
        days_left = remaining.days
        hours_left = remaining.seconds // 3600
        
        text = f"""👤 **প্রিমিয়াম ইউজারের তথ্য:**

**📋 ব্যক্তিগত তথ্য:**
• **নাম:** {name}
• **ইউজার ID:** `{user_id}`
• **Username:** {username}

**💎 প্রিমিয়াম তথ্য:**
• **মেয়াদ শেষ:** `{details['expiry_time'].strftime('%d/%m/%Y %H:%M')}`
• **বাকি সময়:** **{days_left} দিন {hours_left} ঘন্টা**
• **ফ্রি ট্রায়াল:** {'✅ হ্যাঁ' if details['has_free_trial'] else '❌ না'}

**📊 ব্যবহারের তথ্য:**
• **আজকের রিকুয়েস্ট:** `{details['daily_requests']}`
• **মোট রিকুয়েস্ট:** `{details['total_requests']}`
• **দৈনিক সীমা:** `{details['max_daily_requests']}`"""

        buttons = [
            [InlineKeyboardButton("➕ মেয়াদ বাড়ান", callback_data=f"extend_user_{user_id}"),
             InlineKeyboardButton("❌ সরান", callback_data=f"remove_user_{user_id}")],
            [InlineKeyboardButton("🔄 রিফ্রেশ", callback_data=f"refresh_info_{user_id}"),
             InlineKeyboardButton("❌ বন্ধ", callback_data="close_data")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        
    except Exception as e:
        await query.answer(f"❌ এরর: {str(e)}", show_alert=True)

@Client.on_callback_query(filters.regex("close_data"))
async def close_callback(client, query: CallbackQuery):
    """Close the message"""
    await query.message.delete()