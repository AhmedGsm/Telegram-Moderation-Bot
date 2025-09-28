import asyncio
import json
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto
from constants import *
import time
import random


class TelegramPostManager:
    def __init__(self, api_id, api_hash, bot_token, source_group, backup_group, admin_id):
        self.client = TelegramClient("StringSession()", api_id, api_hash)
        self.bot_token = bot_token
        self.source_group = source_group
        self.backup_group = backup_group
        self.admin_id = admin_id
        self.pending_albums = {}  # Track album groupings
        self.user_id = -1000
        self.full_post = False
        self.notification_message = ""
        self.max_image_process_time = 1
        self.images_album_counted = 0
        self.mTime = 0
        self.album_messages = []
        self.is_album_processed = False

    async def start(self):
        await self.client.start(bot_token=self.bot_token)
        print("Bot started successfully")
        self.client.add_event_handler(self.handle_new_message, events.NewMessage(chats=self.source_group))
        await self.client.run_until_disconnected()

    async def handle_new_message(self, event):
        self.mTime = time.time()
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
                print("event.message.grouped_id: " + str(event.message.grouped_id))
                interval = time.time() - self.mTime
                print("interval Time: " + str(interval))
                if interval < self.max_image_process_time:
                    self.images_album_counted += 1
                    print("An image is added album--> Image N: " + str(self.images_album_counted))
                    self.album_messages.append(event.message)

                    await asyncio.sleep(5)

                    if not self.is_album_processed : # and self.images_album_counted > 10
                        self.is_album_processed = True
                        await self.process_album(event)
                        self.images_album_counted = 0
                else:
                    self.album_messages = []
                    self.is_album_processed = False
                    print("A new album is ulpoading..: " + str(self.images_album_counted))


        except Exception as e:
            print(f"Error processing message: {e}")

    async def process_album(self, event):
        """Handle media albums by grouping them"""
        # Sort by ID to maintain original order
        self.album_messages.sort(key=lambda msg: msg.id)

        # If a user is posted image or album plus text enable posting,
        # Else disable posting
        if self.images_album_counted > 10:
            self.full_post = True
        else:
            await self.check_if_full_post(event)

        # Forward album to backup
        if self.full_post:
            await self.client.forward_messages(
                entity=self.backup_group,
                messages=[msg.id for msg in self.album_messages],
                from_peer=self.source_group
            )

        # Delete all album parts
        await self.client.delete_messages(self.source_group, [msg.id for msg in self.album_messages])

        # Reset album precessing state
        #await asyncio.sleep(1)
        self.is_album_processed = False
        self.full_post = False
        # Send notification
        await self.notify_user(event, self.notification_message)


    async def check_if_full_post(self, event):
        """if self.images_album_counted > 10:
            self.notification_message = NOTIFICATION_NO_MORE_TEN_IMAGES
            self.full_post = False"""
        if event.message.message and event.message.media:
            self.notification_message = NOTIFICATION_HIDE_FOR_MODERATION
            self.full_post = True
        elif event.message.media:
            self.full_post = False
            self.notification_message = NOTIFICATION_INSERT_PRODUCT_DEF
        elif event.message.message:
            self.full_post = False
            self.notification_message = NOTIFICATION_NO_QUESTIONS

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
    with open("config/config.json") as f:
        config = json.load(f)

    # Extract values
    API_ID = config["TELEGRAM_API_ID"]
    API_HASH = config["TELEGRAM_API_HASH"]
    BOT_TOKEN = config["TELEGRAM_BOT_TOKEN"]
    SOURCE_GROUP_ID = config["SOURCE_GROUP"]
    BACKUP_GROUP_ID = config["BACKUP_GROUP"]
    ADMIN_SENDER_ID = config["ADMIN_SENDER_ID"]

    manager = TelegramPostManager(
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        source_group=SOURCE_GROUP_ID,
        backup_group=BACKUP_GROUP_ID,
        admin_id=ADMIN_SENDER_ID
    )

    asyncio.run(manager.start())