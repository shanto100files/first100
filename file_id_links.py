from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from urllib.parse import quote_plus
import hashlib

# Configuration
from info import URL
WORKER_URL = URL.rstrip('https://odd-darkness-074fsadsafsafasfjlknmmlkaytr9pe8afnhdklnfalskdftgy.bdmovieshub.workers.dev/')  # Use the same URL as your main bot

# Function to get file name
def get_name(message):
    if message.document:
        return message.document.file_name
    elif message.video:
        return message.video.file_name
    elif message.audio:
        return message.audio.file_name
    elif message.voice:
        return "voice.ogg"
    elif message.video_note:
        return "video_note.mp4"
    elif message.animation:
        return message.animation.file_name
    else:
        return "file"

# Function to generate permanent links using file_id
def generate_file_id_links(message):
    try:
        # Get file ID directly
        if isinstance(message, dict):
            # Handle dictionary input (for direct file_id usage)
            media_type = message.get('media', '')
            if media_type == 'document':
                file_id = message['document']['file_id']
                file_name = message['document'].get('file_name', 'file')
            elif media_type == 'video':
                file_id = message['video']['file_id']
                file_name = message['video'].get('file_name', 'video.mp4')
            elif media_type == 'audio':
                file_id = message['audio']['file_id']
                file_name = message['audio'].get('file_name', 'audio.mp3')
            else:
                return None
        else:
            # Handle message object
            if hasattr(message, 'document') and message.document:
                file_id = message.document.file_id
                file_name = message.document.file_name
            elif hasattr(message, 'video') and message.video:
                file_id = message.video.file_id
                file_name = message.video.file_name
            elif hasattr(message, 'audio') and message.audio:
                file_id = message.audio.file_id
                file_name = message.audio.file_name
            elif hasattr(message, 'voice') and message.voice:
                file_id = message.voice.file_id
                file_name = "voice.ogg"
            elif hasattr(message, 'video_note') and message.video_note:
                file_id = message.video_note.file_id
                file_name = "video_note.mp4"
            elif hasattr(message, 'animation') and message.animation:
                file_id = message.animation.file_id
                file_name = message.animation.file_name
            else:
                return None

        # URL encode the file name
        encoded_file_name = quote_plus(file_name)

        # Create permanent links using file_id
        permanent_stream = f"{WORKER_URL}/stream/{file_id}/{encoded_file_name}"
        permanent_download = f"{WORKER_URL}/file/{file_id}/{encoded_file_name}"

        # Create buttons
        buttons = [
            [
                InlineKeyboardButton("🔗 PERMANENT DOWNLOAD 🔗", url=permanent_download)
            ],
            [
                InlineKeyboardButton("🎬 PERMANENT STREAM 🎬", url=permanent_stream)
            ],
            [
                InlineKeyboardButton("📱 WATCH IN APP 📱", web_app=WebAppInfo(url=permanent_stream))
            ]
        ]

        return {
            "file_id": file_id,
            "file_name": file_name,
            "stream_link": permanent_stream,
            "download_link": permanent_download,
            "buttons": buttons
        }
    except Exception as e:
        print(f"Error generating file ID links: {e}")
        return None

# Example command to get permanent links
@Client.on_message(filters.command("getfilelink") & filters.private)
async def get_file_link_command(client, message):
    if not message.reply_to_message or not message.reply_to_message.media:
        await message.reply_text("Reply to a media message to get permanent file ID links.")
        return

    # Generate links
    links = generate_file_id_links(message.reply_to_message)

    if links:
        await message.reply_text(
            text=f"**Here are your permanent file ID links:**\n\n"
                 f"**File:** {links['file_name']}\n"
                 f"**File ID:** `{links['file_id']}`\n\n"
                 f"These links will never expire and will always work!",
            reply_markup=InlineKeyboardMarkup(links["buttons"])
        )
    else:
        await message.reply_text("Failed to generate permanent links.")

# Function to add to your existing pm_filter.py
async def add_file_id_links_to_results(client, query, results):
    for result in results:
        # Get the file ID from the result
        file_id = result.document.file_id if result.document else result.video.file_id if result.video else None

        if file_id:
            # Get the file name
            file_name = get_name(result)
            encoded_file_name = quote_plus(file_name)

            # Create permanent links
            permanent_stream = f"{WORKER_URL}/stream/{file_id}/{encoded_file_name}"
            permanent_download = f"{WORKER_URL}/file/{file_id}/{encoded_file_name}"

            # Add buttons to the result
            result.reply_markup.inline_keyboard.extend([
                [
                    InlineKeyboardButton("🔗 PERMANENT LINK 🔗", url=permanent_stream)
                ]
            ])

    return results

# How to integrate with your existing code:
# 1. Add the generate_file_id_links function to your bot
# 2. Add the /getfilelink command handler
# 3. Modify your existing inline query handler to add file ID links
# 4. Deploy the file-id-worker.js to Cloudflare Workers
