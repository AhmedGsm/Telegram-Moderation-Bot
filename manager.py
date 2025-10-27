import asyncio
import json
from collections import defaultdict

from telethon import TelegramClient, events, Button
from moderator import ContentModerator

class TelegramPostManager:
    def __init__(self, api_id, api_hash, bot_token, source_group, backup_group, admin_id):
        self.client = TelegramClient(str(admin_id), api_id, api_hash)
        self.bot_token = bot_token
        self.source_group = source_group
        self.backup_group = backup_group
        self.admin_id = admin_id
        self.users = defaultdict(lambda: ContentModerator(self.client, self.source_group, self.backup_group, self.admin_id))
        self.lock = asyncio.Lock()
        self.album_event = None

    async def fetch_users_from_group(self, group_id, limit):
        # Start the client
        #await self.client.start()
        # Replace 'group_name' with your group's name or ID
        group = await self.client.get_entity(group_id)

        # Fetch the last 100 messages from the group (adjust limit as needed)
        messages = await self.client.get_messages(group, limit=limit)

        # Loop through the messages and filter media messages
        for msg in messages:
            # Check if the message contains media (photo/video)
            if msg.media:
                grouped_id = msg.grouped_id  # This is the unique ID for albums
                sender_id = msg.sender_id

                # If the message has a grouped_id, it's part of an album
                if grouped_id:
                    # Append the message ID to the list of the corresponding album
                    user = self.users.setdefault(
                        sender_id,
                        ContentModerator(self.client, self.source_group, self.backup_group, self.admin_id)
                    )
                    user.albums[grouped_id].append(msg.id)


    async def handle_new_message_on_source_group(self, event):
        print(f"handle_new_message_on_source_group Event type: {type(event)}")
        # Let the admin to post and forwar
        with open("config/config.json") as f:
            config = json.load(f)
        admin_id = int(config["ADMIN_SENDER_ID"])

        user_id = event.message.from_id.user_id
        if user_id == admin_id:
            return

        # Get user details
        sender = await event.get_sender()
        user_id = sender.id

        # Create User Instance
        async with self.lock:
            user = self.users.setdefault(
                user_id,
                ContentModerator(self.client, self.source_group, self.backup_group, self.admin_id)
            )

        # Process album
        await user.process_message(event)

    async def handle_new_message_on_backup_group(self, event):
        print(f"handle_new_message_on_backup_group Event type: {type(event)}")
        print("start_handler")
        print("event message ID " + str(event.message.id))

        # Check if it is an album if the counter is 2
        # Cancel Processing let the album event work !
        user = self.users.setdefault(
            event.message.from_id.user_id,
            ContentModerator(self.client, self.source_group, self.backup_group, self.admin_id)
        )

        user.message_counter += 1
        if user.message_counter == 2:
            user.is_it_album = True
            return

        # Wait other message
        await asyncio.sleep(0)
        if user.is_it_album:
            #self.message_counter = 0
            #self.is_it_album = False
            return

        # Build message text
        await self.show_notification_menu(event)
        user.message_counter = 0
        user.is_it_album = False

    async def handle_new_album_on_backup_group(self, event: events.Album.Event):
        print(f"handle_new_album_on_backup_group Event type: {type(event)}")
        print("album_handler Album is uploaded!")
        self.album_event = event
        await self.show_notification_menu(event)

        user = self.users.setdefault(
            event.sender_id,
            ContentModerator(self.client, self.source_group, self.backup_group, self.admin_id)
        )

        user.message_counter = 0
        user.is_it_album = False

    async def show_notification_menu(self, event):
        text = (
            "✨ <b>Welcome!</b>\n"
            "I'm alive and glowing.\n\n"
            "Choose what you want to do next 👇"
        )
        # Build chat and message ids
        try:
            message_id = event.message.id
            message_type = "message"
        except:
            grouped_id = event.grouped_id
            message_type = "album"
            user = self.users.setdefault(
                event.sender_id,
                ContentModerator(self.client, self.source_group, self.backup_group, self.admin_id)
            )

            user.albums[grouped_id] = [msg.id for msg in event.messages]
            message_id = grouped_id

        # Build inline keyboard
        keyboard = [
            [
                Button.inline("✅ Approve", f"approve:{message_id}:{message_type}".encode()),
                Button.inline("🚫 Reject", f"reject:{message_id}:{message_type}".encode())
            ]
        ]


        # Display notification
        await event.respond(
            text,
            buttons=keyboard,
            parse_mode="html"
        )

    @events.register(events.CallbackQuery)
    async def callback_handler(self, event):
        print(f"callback_handler Event type: {type(event)}")
        data = event.data.decode("utf-8")
        # Album Event
        album_event = self.album_event
        # Example: "approve:12345"
        action, message_id, message_type = data.split(":")

        # "approve" button logic
        if action == "approve":
            # Edit original message text + remove buttons
            await event.edit(
                "✅ <b>Approved!</b>\n"
                "Action has been registered successfully.",
                buttons=None,
                parse_mode="html"
            )
            # Optional popup
            await event.answer("Approved ✔", alert=True)

            # Resend the post to the original Group
            await event.client.forward_messages(
                entity=self.source_group,
                messages=[int(message_id)],
                from_peer=self.backup_group
            )


        # "reject" button logic
        elif action == "reject":
            await event.edit(
                "❌ <b>Rejected.</b>\n"
                "The item will not be published.",
                buttons=None,
                parse_mode="html"
            )
            await event.answer("Rejected ❌", alert=True)

            #await user_event.delete()

        # "more" button logic

        # Delete user message if it is rejected!
        # If it is an Album
        chat_id = event.chat_id
        user_id = event.sender_id
        msg_id = int(message_id)
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

    async def start(self):
        await self.client.start()
        print("Bot started successfully")

        await self.fetch_users_from_group(self.backup_group, 1000)

        # Register handlers
        self.client.add_event_handler(self.handle_new_message_on_source_group,
                                      events.NewMessage(chats=self.source_group))
        self.client.add_event_handler(self.handle_new_message_on_backup_group,
                                      events.NewMessage(chats=self.backup_group))
        self.client.add_event_handler(self.handle_new_album_on_backup_group, events.Album(chats=self.backup_group))
        self.client.add_event_handler(self.callback_handler)

        # Run non continuously
        await self.client.run_until_disconnected()



