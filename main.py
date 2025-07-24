
import asyncio
import os

from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto
from constants import *


class TelegramPostManager:
    def __init__(self, api_id, api_hash, bot_token, source_group, backup_group, admin_id):
        self.client = TelegramClient('bot_session', api_id, api_hash)
        self.bot_token = bot_token
        self.source_group = source_group
        self.backup_group = backup_group
        self.admin_id = admin_id
        self.pending_albums = {}  # Track album groupings
        self.user_id = -1000
        self.full_post = False
        self.notification_message = ""

    async def start(self):
        await self.client.start(bot_token=self.bot_token)
        print("Bot started successfully")
        self.client.add_event_handler(self.handle_new_message, events.NewMessage(chats=self.source_group))
        await self.client.run_until_disconnected()

    async def handle_new_message(self, event):
        # Ignore messages from Haris_BOT to prevent infinite loop
        if event.message.from_id.user_id == 8162000565:
            return

        # Get user details
        sender = await event.get_sender()
        self.user_id = sender.id
        username = sender.username or sender.first_name
        print(f"User ID: {self.user_id}, Username: @{username}")

        try:
            # Ignore service messages and bot commands
            if not event.message.message and not event.message.media:
                return


            # Handle media albums
            if self.user_id != self.admin_id:
                if event.message.grouped_id:
                    print("Processing album!!")
                    await self.process_album(event)
                # Handle single messages
                else:
                    await self.process_single_message(event)

        except Exception as e:
            print(f"Error processing message: {e}")

    async def check_if_full_post(self, event):
        self.full_post = False
        self.notification_message = NOTIFICATION_IMAGE_TEXT
        if event.message.message and event.message.media:
            self.notification_message = NOTIFICATION_HIDE_FOR_MODERATION
            self.full_post = True

    async def process_single_message(self, event):
        """Process non-album messages"""
        # Copy to backup group

        # If a user is posted image or album plus text enable posting,
        # Else disable posting
        await self.check_if_full_post(event)

        if self.full_post:
            await self.client.forward_messages(
                entity=self.backup_group,
                messages=event.message.id,
                from_peer=self.source_group
            )

        # Delete from source group
        await event.message.delete()

        # Send notification
        await self.notify_user(event, self.notification_message)

    async def process_album(self, event):
        """Handle media albums by grouping them"""
        album_id = event.message.grouped_id
        album_messages = self.pending_albums.setdefault(album_id, [])
        album_messages.append(event.message)

        # Wait 1 second to collect all album parts
        await asyncio.sleep(1)
        if album_id not in self.pending_albums:
            return

        messages = self.pending_albums.pop(album_id)

        # Sort by ID to maintain original order
        messages.sort(key=lambda msg: msg.id)

        # If a user is posted image or album plus text enable posting,
        # Else disable posting
        await self.check_if_full_post(event)

        # Forward album to backup
        if self.full_post:
            await self.client.forward_messages(
                entity=self.backup_group,
                messages=[msg.id for msg in messages],
                from_peer=self.source_group
            )

        # Delete all album parts
        await self.client.delete_messages(self.source_group, [msg.id for msg in messages])

        # Send notification
        await self.notify_user(event, self.notification_message)

    async def forward_album(self, messages):
        """Forward entire album preserving grouping"""
        media = []
        caption = ""

        for msg in messages:
            if msg.message:
                caption = msg.message
            if isinstance(msg.media, MessageMediaPhoto):
                media.append(msg.media)

        await self.client.send_file(
            self.backup_group,
            media,
            caption=caption,
            link_preview=False
        )

    async def notify_user(self, event, message):
        """Notify user about hidden post"""
        sender = await event.get_sender()
        username = sender.username or sender.first_name
        notification = await self.client.send_message(
            self.source_group,
            f"@{username} {message}",
            reply_to=event.message.reply_to_msg_id
        )
        # Wait 5 seconds (or 10 if you prefer)
        await asyncio.sleep(DELETE_NOTIFICATION_DELAY)

        # Delete the notification message
        try:
            await self.client.delete_messages(self.source_group, [notification.id])
            print("Message notification deleted!!")
        except Exception as e:
            print(f"Failed to delete notification: {e}")



if __name__ == "__main__":
    # Configuration (use environment variables in production)
    from dotenv import load_dotenv

    load_dotenv()
    API_ID = int(os.getenv("TELEGRAM_API_ID"))
    API_HASH = os.getenv("TELEGRAM_API_HASH")
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    SOURCE_GROUP_ID = int(os.getenv("SOURCE_GROUP"))
    BACKUP_GROUP_ID = int(os.getenv("BACKUP_GROUP"))
    ADMIN_SENDER_ID = int(os.getenv("ADMIN_SENDER_ID"))

    manager = TelegramPostManager(
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        source_group=SOURCE_GROUP_ID,
        backup_group=BACKUP_GROUP_ID,
        admin_id=ADMIN_SENDER_ID
    )

    asyncio.run(manager.start())