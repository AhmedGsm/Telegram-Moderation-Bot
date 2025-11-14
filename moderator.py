import asyncio
from collections import defaultdict
from telethon.tl.types import Message
from constants import *
from utils import Utils


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
        self.albums = defaultdict(list)
        self.is_album_on_source = False
        self.start_time_on_source = -1
        self.is_album_on_backup = False
        self.start_time_on_backup = -1

    async def process_message(self, event):
        print("def process_message")
        # Check if the event is a single message or part of an album
        event_message = None
        try:
            try:
                # If it is single message
                if event.message:
                    event_message = event.message
                    messages = [event_message]
            except:
                # If it is an album
                messages = event.messages
                event_message = messages[0]
            # Ignore service messages and bot commands
            if not event_message.message and not event_message.media:
                return

            # Handle media albums
            # Forward only non admin messages

            # Retrieve user ID
            user_id = event_message.sender.id

            # Get the list of participants in the chat
            participants = await self.client.get_participants(self.source_group)

            # Check if the user is an admin
            for p in participants:
                if user_id != p.id:
                    continue
                try:
                    if p.participant.admin_rights:
                        pass
                    return
                except:
                    #print(str(p.id) + " IS NOT AN ADMIN")
                    break


            #is_admin = any(p.id == user_id and p.is_admin for p in participants)
            # If the poster is an admin then don't forward album to backup moderation group

            await self.client.forward_messages(
                entity=self.backup_group,
                messages=[msg.id for msg in messages],
                from_peer=self.source_group
            )

            print("Album forwarded (self.client.forward_messages)")
            await self.delete_post_and_notify(event)

        except Exception as e:
            print(f"Error processing message: {e}")


    async def delete_post_and_notify(self, event):
        # Delete all album parts
        await event.delete()
        #await self.client.delete_messages(self.source_group, [msg.id for msg in album])
        # Send notification
        #await self.notify_user(event, self.notification_message)
        await Utils.notify_user(self.client, self.source_group, event, self.notification_message, DELETE_NOTIFICATION_DELAY)

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
