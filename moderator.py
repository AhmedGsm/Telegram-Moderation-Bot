import asyncio
from constants import *


class ContentModerator:
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
        self.message_counter = 0
        self.is_it_album = False
        self.albums = {}

    async def process_message(self, event):
        print("def process_message")
        try:
            # Ignore service messages and bot commands
            if not event.message.message and not event.message.media:
                return

            # Handle media albums
            if self.user_id != self.admin_id:
                await self.process_album(event)

        except Exception as e:
            print(f"Error processing message: {e}")

    async def process_album(self, event):
        """Handle media albums by grouping them"""
        print("def process_album")
        # Group Id of a message
        message_group_id = event.message.grouped_id

        # Check if text is uploaded
        if event.message.message:
            self.is_text_uploaded = True

        # Check if image or media is uploaded
        if event.message.media:
            self.is_media_uploaded = True

        if not message_group_id:# Text message
            self.album_dict["single"].append(event.message)
        else:
            self.album_dict.setdefault(message_group_id, []).append(event.message)

        # Forward album to backup
        if not self.is_album_processed:
            self.is_album_processed = True
            # Send Album
            await self.send_album(event)

    async def send_album(self, event):
        print("def send_album")
        # Wait to allow processing next images to be added to album
        await asyncio.sleep(3)

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
