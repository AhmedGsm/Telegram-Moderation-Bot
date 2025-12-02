import asyncio
from collections import defaultdict
from constants import *
from userdb import UserDB
from utils import Utils

class ContentModerator:
    def __init__(self, client, source_group, backup_group, admin_id):
        self.pending_albums = {}
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
        self.db = UserDB()

    async def process_message(self, event):
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
                    break

            # Check if user poster trusted by admin
            if self.db.get_user(user_id, "trust")["trust"] == "trusted":
                return

            await self.client.forward_messages(
                entity=self.backup_group,
                messages=[msg.id for msg in messages],
                from_peer=self.source_group
            )

            await self.delete_post_and_notify(event)

        except Exception as e:
            Utils.create_logger().error(f"{ERROR_PROCESSING_MESSAGE} {e}")


    async def delete_post_and_notify(self, event):
        # Delete all album parts
        await event.delete()
        # Send notification
        await Utils.notify_user(self.client, self.source_group, event, self.notification_message, DELETE_NOTIFICATION_DELAY)
