import asyncio
import json
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto
from constants import *
import time
import random

class User:
    def __init__(self, client, source_group, backup_group, admin_id):
        self.pending_albums = {}  # Track album groupings
        self.user_id = -1000
        self.source_group = source_group
        self.backup_group = backup_group
        self.admin_id = admin_id
        self.client = client
        self.notification_message = NOTIFICATION_HIDE_FOR_MODERATION
        self.album_messages = []
        self.is_album_processed = False
        self.album_dict = {"single": []
                           }
        self.require_image_and_text = False
        self.task = None
        self.timeout = 2

    async def process_message(self, event):
        print("def process_message")
        #try:
        # Ignore service messages and bot commands
        if not event.message.message and not event.message.media:
            return

        # Handle media albums
        if self.user_id != self.admin_id:

            # Start a new debounce timer
            previousTime = time.time()
            self.task = asyncio.create_task(self.process_album(event))
            #print("asyncio.create_task running time is: " + str(time.time() - previousTime))
            #tsk = self.task
            #if tsk:
            #    print("task is created and is not None!!")

            #print("self.task returns: " + str(tsk))
            # Start a moment to let task to be assigned
            #await asyncio.sleep(0.5)

        #except Exception as e:
        #    print(f"Error processing message: {e}")

    async def process_album(self, event):
        """Handle media albums by grouping them"""
        print("def process_album")
        # Sort by ID to maintain original order
        #self.album_messages.sort(key=lambda msg: msg.id)
        # Cancel any pending task
        # Group Id of a message
        message_group_id = event.message.grouped_id

        # Check if text is uploaded
        if event.message.message:
            self.is_text_uploaded = True

        # Check if image or media is uploaded
        if event.message.media:
            self.is_media_uploaded = True

        # If a user is posted image or album plus text enable posting,
        # Else disable posting
        if not message_group_id:# Text message
            self.album_dict["single"].append(event.message)
        else:
            self.album_dict.setdefault(message_group_id, []).append(event.message)

        # Pause a moment
        #await asyncio.sleep(3)
        """try:
            await asyncio.sleep(self.timeout)
            print("task completed(timeout reached !!")
        except asyncio.CancelledError:
            print("asyncio.CancelledError")
            return  # restarted, so ignore"""

        # Forward album to backup
        if not self.is_album_processed:
            self.is_album_processed = True
            # Send Album
            await self.send_album(event)

    async def send_album(self, event):
        print("def send_album")
        # Jump to previous task then run the below code!!
        await asyncio.sleep(3)
        # Cancel previous task to assign full album
        """if self.task : #and not self.task.done()
            self.task.cancel()
            print("self.task = " + str(self.task))
            print("task canceled --> going to return!!")
            return
        else:
            print("self.task = None")"""

        for album in self.album_dict.values():
            album.sort(key=lambda msg: msg.id)
            if album:
                await self.client.forward_messages(
                    entity=self.backup_group,
                    messages=[msg.id for msg in album],
                    from_peer=self.source_group
                )

                print("Album forwarded (self.client.forward_messages)")
        await self.delete_post_and_notify(event)
        #await asyncio.sleep(0.5)
        self.album_dict = {"single": [],
                           }
        self.is_album_processed = False

    async def delete_post_and_notify(self, event):
        # Delete all album parts
        for album in self.album_dict.values():
            if album:
                await self.client.delete_messages(self.source_group, [msg.id for msg in album])
        # Send notification
        await self.notify_user(event, self.notification_message)

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



class TelegramPostManager:
    def __init__(self, api_id, api_hash, bot_token, source_group, backup_group, admin_id):
        self.client = TelegramClient("StringSession()", api_id, api_hash)
        self.bot_token = bot_token
        self.source_group = source_group
        self.backup_group = backup_group
        self.admin_id = admin_id
        self.users_instances = {}
        self.lock = asyncio.Lock()

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
        user_id = sender.id
        username = sender.username or sender.first_name
        #print(f"User ID: {user_id}, Username: @{username}")

        # Create User Instance
        async with self.lock:
            user_instance = self.users_instances.setdefault(
                user_id,
                User(self.client, self.source_group, self.backup_group, self.admin_id)
            )

        # Process album
        await user_instance.process_message(event)

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