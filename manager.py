import asyncio

import json
import time
from collections import defaultdict

from telethon import TelegramClient, events, Button

from constants import *
from moderator import ContentModerator
from userdb import UserDB
from utils import Utils


class TelegramPostManager:
    def __init__(self, api_id, api_hash, bot_token, source_group, backup_group, admin_id):
        self.client = TelegramClient(Utils.hash_session_name(admin_id, "bot"),
                                     api_id, api_hash)
        self.user_client = None
        with open("config/config.json") as f:
            self.config = json.load(f)
        self.bot_id = -1
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.source_group = source_group
        self.backup_group = backup_group
        self.admin_id = admin_id
        self.users = defaultdict(lambda: ContentModerator(self.client, self.source_group, self.backup_group, self.admin_id))
        self.lock = asyncio.Lock()
        self.album_event = None
        self.user_event = None
        self.previous_time = time.time()
        self.time_2_message = 0.1
        self.is_notification_shown = False
        self.db = UserDB()

    async def fetch_users_from_group(self, group_id, limit):
        # Start the client to fetch group messages
        # Generate a unique session name by hashing the admin_id


        self.user_client = TelegramClient(Utils.hash_session_name(self.admin_id, "user"),
                                              self.api_id, self.api_hash)
        await self.user_client.start()
        # Replace 'group_name' with your group's name or ID
        group = await self.user_client.get_entity(group_id)

        # Fetch the last 100 messages from the group (adjust limit as needed)
        messages = await self.user_client.get_messages(group, limit=limit)

        # Loop through the messages and filter media messages
        for msg in messages:
            # Check if the message contains media (photo/video)
            if msg.media:
                grouped_id = msg.grouped_id  # This is the unique ID for albums
                sender_id = msg.sender_id
                forwarder_id = msg.forward.sender_id

                # If the message has a grouped_id, it's part of an album
                if grouped_id:
                    # Append the message ID to the list of the corresponding album
                    user = self.users.setdefault(
                        forwarder_id,
                        ContentModerator(self.client, self.source_group, self.backup_group, self.admin_id)
                    )
                    user.albums[grouped_id].append(msg.id)

    async def get_sender(self, event, client):
        user = self.users.setdefault(
            event.sender_id,
            ContentModerator(client, self.source_group, self.backup_group, self.admin_id)
        )
        return user

    async def filter_single_message_detection(self, user, group: str):
        if group == "source":
            is_album_attr = "is_album_on_source"
            start_attr = "start_time_on_source"
        elif group == "backup":
            is_album_attr = "is_album_on_backup"
            start_attr = "start_time_on_backup"
        else:
            print("Unknown group name -- Filtering single message detection")
            return

        # get current values dynamically
        is_album = getattr(user, is_album_attr)
        start_time = getattr(user, start_attr)

        if is_album:
            return -1

        if start_time < 0:
            # assign by reference using setattr
            setattr(user, start_attr, time.time())
        else:
            diff = time.time() - start_time
            print(f"Diff between 2 msgs: {diff:.2f}s")
            if diff < SINGLE_MESSAGE_DETECTION_TIMEOUT:
                setattr(user, is_album_attr, True)
                return -1
            # update start time after valid message
            setattr(user, start_attr, time.time())

        await asyncio.sleep(0)

        if getattr(user, is_album_attr):
            return -1

        """setattr(user, is_album_attr, False)
        setattr(user, start_attr, -1)"""
        return 0

    async def handle_new_message_on_source_group(self, event):
        print(f"handle_new_message_on_source_group Event type: {type(event)}")

        user = await self.get_sender(event, self.client)

        if await self.filter_single_message_detection(user, "source") == -1:
            return

        """actual_time = time.time()
        time_between_messages = actual_time - self.previous_time
        if time_between_messages <= self.time_2_message:
            return
        print("Time elapsed: " + str(time_between_messages))
        self.previous_time = actual_time"""


        await user.process_message(event)

        # add user to db
        telegram_user = await event.get_sender()
        self.db.ensure_user(telegram_user)

        user.is_album_on_source = False
        user.start_time_on_source = -1

    async def handle_new_message_on_backup_group(self, event):

        await asyncio.sleep(0.2)
        print(f"handle_new_message_on_backup_group Event type: {type(event)}")

        if event.message.from_id.user_id != self.bot_id:

        #if not event.message.from_id.user_id == self.bot_id: #or

            # Delete notification after moments
            await event.delete()

            # No posting allowed notification
            print(NOTIFICATION_NO_DIRECT_POSTING_IN_BACKUP_GROUP)
            await Utils.notify_user(self.client, self.backup_group, event,
                                    NOTIFICATION_NO_DIRECT_POSTING_IN_BACKUP_GROUP,
                                    DELETE_NOTIFICATION_DELAY)

            return

        # If the message is not forwarded from the source group then don't display notification
        if not event.message.forward:
            return
        """if event.message.forward:
            pass
        if not event.message.fwd_from:
            print("Direct message not allowed in the backup group, only bot allowed to forward!")
            return"""

        user = await self.get_sender(event, self.client)

        if await self.filter_single_message_detection(user, "backup") == -1:
            return

        await self.show_notification_menu(event)

        await self.reset_attributes(user)

    async def handle_new_album_on_source_group(self, event):
        user = await self.get_sender(event, self.client)
        print(" ".join(["Album detected within" , str(time.time() - user.start_time_on_source), "seconds"]))
        user.is_album_on_source = True
        print("album_handler Album source_group")

        await user.process_message(event)

        # add user to db
        telegram_user = await event.get_sender()
        self.db.ensure_user(telegram_user)

        await self.reset_attributes(user)

        print("Bottom of the handle_new_album_on_source_group function!!!")

    async def reset_attributes(self, user):
        user.is_album_on_source = False
        user.start_time_on_source = -1
        user.is_album_on_backup = False
        user.start_time_on_backup = -1

    async def handle_new_album_on_backup_group(self, event):
        print("Program Starts asyncio.sleep(0.2)")
        await asyncio.sleep(0.2)
        #print(f"handle_new_album_on_backup_group Event type: {type(event)}")
        if not event.messages[0].forward:
            print(f"Direct message detected, skipping.")
            return  # Skip processing forwarded messages


        print("user = await self.get_sender(event, self.client)")
        user = await self.get_sender(event, self.client)
        if not self.is_notification_shown:
            print("self.is_notification_shown = True")
            self.is_notification_shown = True
            print("await self.show_notification_menu(event)")
            await self.show_notification_menu(event)
            return
        print("await self.reset_attributes(user)")
        await self.reset_attributes(user)
        print("self.is_notification_shown = False")
        await asyncio.sleep(0)
        self.is_notification_shown = False


    async def show_notification_menu(self, event):

        # Get User ID
        user_id = event.forward.from_id.user_id
        user_db = self.db.get_user(user_id)
        text = (
            FOOTER_MODERATION_MESSAGE +
            "approved = " + str(user_db["approved_posts"]) + " | "
            "rejected = " + str(user_db["rejected_posts"]) + "\n"
            "\n<b>User stats</b>\n" 
            "warns = " + str(user_db["warn_count"]) + " | "
            "kicks = " + str(user_db["kick_count"]) + " | "
            "mutes = " + str(user_db["mute_count"]) + " | "
            "bans = " + str(user_db["ban_count"]) + ""
        )
        # Build chat and message ids
        try:
            message_id = event.message.id
            message_type = "message"
        except:
            grouped_id = event.grouped_id
            message_type = "album"
            user = self.users.setdefault(
                event.forward.sender_id,
                ContentModerator(self.client, self.source_group, self.backup_group, self.admin_id)
            )

            user.albums[grouped_id] = [msg.id for msg in event.messages]
            message_id = grouped_id

        # Build inline keyboard
        keyboard = [
            [
                Button.inline("✅ Approve post", f"approve:{message_id}:{message_type}".encode()),
                Button.inline("🚫 Reject post", f"reject:{message_id}:{message_type}".encode())
            ],
            [
                Button.inline("⚠ Warn user", f"warn:{user_id}:{message_id}".encode()),
                Button.inline("🔇 Mute user", f"mute:{user_id}:{message_id}".encode())
            ],
            [
                Button.inline("👢 Kick user", f"kick:{user_id}:{message_id}".encode()),
                Button.inline("🚫 Ban user", f"ban:{user_id}:{message_id}".encode())
            ],
            [
                Button.inline("🎖 Trust User", f"trust_user:{message_id}:{message_type}".encode())
            ],
        ]

        # Display notification
        """await event.respond(
            text,
            buttons=keyboard,
            parse_mode="html"
        )"""

        # Send the notification with buttons
        await self.client.send_message(
            self.backup_group,  # Can be chat ID, username, or entity
            text,
            buttons=keyboard,  # Inline buttons
            parse_mode="html"  # Use HTML formatting
        )

    @events.register(events.CallbackQuery)
    async def callback_handler(self, event):
        #print(f"callback_handler Event type: {type(event)}")
        data = event.data.decode("utf-8")
        # Album Event
        album_event = self.album_event
        # Example: "approve:12345"
        action, message_id, message_type = data.split(":")
        chat_id = event.chat_id
        user_id = event.sender_id
        msg_id = int(message_id)

        # "approve" button logic
        if action == "approve":
            # Edit original message text + remove buttons
            await self.show_action_notification(event,"✅ <b>Approved!</b>\n",
                                                "Post has been registered successfully.")

            # Optional popup

            # Resend the post to the original Group
            if message_type == "message":
                messages_ids = [msg_id]
            elif message_type == "album":
                group_id = msg_id
                messages_ids = self.users[user_id].albums[group_id]

            # Forward the Album
            await event.client.forward_messages(
                entity=self.source_group,
                messages=messages_ids,
                from_peer=self.backup_group
            )

            self.db.increment(user_id, "approved_posts")

        # "reject" button logic
        elif action == "reject":
            # Show action notification
            await self.show_action_notification(event,"❌ <b>Rejected.</b>\n",
                                                "The item will not be published.")

            # Send DM message notification
            await self.user_client.send_message(
                user_id,
                f"❌ <b>{event.chat.title}:</b>\n\n Your post is rejected by the admins. Please follow group rules.",
                parse_mode="html"
            )

            self.db.increment(user_id, "rejected_posts")

        elif action == "trust_user":
            self.db.update_entry(user_id, "trust", "trusted")
            await self.show_action_notification(event,"👍 <b>Trust updated .</b>\n",
                                                "User trusted now and he can post without verification!")
        elif action == "warn":
            await self.user_client.send_message(user_id,
                f"<i>{self.source_group}</i> group:" + WARNING_MESSAGE,
                parse_mode="html"
            )

            # Display warning notification
            await self.show_action_notification(event,"⚠ <b>Warning .</b>\n",
                                                "DM Warning has been sent to user .")

            self.db.increment(user_id, "warn_count")
            #self.db.set_state(user_id, "warned")

        elif action == "kick":
            try:
                # Kick the user one time
                await self.client.kick_participant(self.source_group, user_id)

                # Display action notification
                await self.show_action_notification(event, "❌ <b>User Kicked .</b>\n",
                                                    "User has been kicked .")

                # Send DM message
                # Send kick DM message
                await self.user_client.send_message(user_id, f"<i>{self.source_group}</i> group:" + KICK_MESSAGE, parse_mode="html")

            except Exception as e:
                await self.show_action_notification(event, "❌ <b>User Kick .</b>\n",
                                                    "Failed to kick user .")
                return

            self.db.increment(user_id, "kick_count")
            self.db.set_state(user_id, "kicked")

        elif action == "mute":
            await self.user_client.edit_permissions(
                self.source_group,
                user_id,
                send_messages=False
            )
            await self.show_action_notification(event,"⚠ <b>User Muted .</b>\n",
                                                "User has been muted .")

            self.db.increment(user_id, "mute_count")
            self.db.set_state(user_id, "muted")

        elif action == "ban":
            await self.user_client.edit_permissions(
                self.source_group,
                user_id,
                view_messages=False)
            """
            await self.user_client.edit_permissions(
                self.source_group,
                8324555069,
                view_messages=True,
                send_messages=True
            )
            """

            await self.show_action_notification(event,"❌ <b>User banned.</b>\n",
                                                "User has been banned.")
            # Send DM message

            # Send kick DM message
            await self.user_client.send_message(user_id, f"<i>{self.source_group}</i> group:" + BAN_MESSAGE, parse_mode="html")

            self.db.increment(user_id, "ban_count")
            self.db.set_state(user_id, "banned")

        # "more" button logic

        # Delete user message if it is rejected!
        # If it is an Album
        if message_type == "message":
            await event.client.delete_messages(chat_id, msg_id)
        elif message_type == "album":
            user = self.users[event.sender_id]

            # Delete images with a loop
            for m_id in user.albums[msg_id]:
                await event.client.delete_messages(chat_id, m_id)

            # Delete album and its content from user
            del user.albums[msg_id]

        await asyncio.sleep(2)

        # Delete message notification
        await event.delete()

    async def show_action_notification(self, event, title, text):
        await event.edit(
            f"{title}\n{text}",
            buttons=None,
            parse_mode="html"
        )

    async def start(self):

        await self.client.start(bot_token=self.bot_token)
        self.bot_id = (await self.client.get_me()).id
        await self.fetch_users_from_group(self.backup_group, 1000)
        print("Bot started successfully")

        # Register handlers
        self.user_client.add_event_handler(self.handle_new_album_on_source_group,
                                           events.Album(chats=self.source_group))
        self.user_client.add_event_handler(self.handle_new_message_on_source_group,
                                      events.NewMessage(chats=self.source_group))
        self.user_client.add_event_handler(self.handle_new_message_on_backup_group,
                                      events.NewMessage(chats=self.backup_group)) #, forwards=True
        self.user_client.add_event_handler(self.handle_new_album_on_backup_group,
                                           events.Album(chats=self.backup_group))
        self.client.add_event_handler(self.callback_handler)

        # Run non continuously
        await self.user_client.run_until_disconnected()
        await self.client.run_until_disconnected()



