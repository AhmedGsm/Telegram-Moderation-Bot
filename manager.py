import asyncio
import json
from telethon import TelegramClient, events, Button
from moderator import ContentModerator

class TelegramPostManager:
    def __init__(self, api_id, api_hash, bot_token, source_group, backup_group, admin_id):
        self.client = TelegramClient("StringSession()", api_id, api_hash)
        self.bot_token = bot_token
        self.source_group = source_group
        self.backup_group = backup_group
        self.admin_id = admin_id
        self.users = {}
        self.lock = asyncio.Lock()


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

    async def handle_new_album_on_backup_group(self, event):
        print(f"handle_new_album_on_backup_group Event type: {type(event)}")
        print("album_handler Album is uploaded!")
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
            chat_id = event.message.chat_id
            message_id = event.message.id
            message_type = "message"
        except:
            chat_id = event.chat_id
            message_id = event.grouped_id
            message_type = "album"

        # Build inline keyboard
        keyboard = [
            [
                Button.inline("✅ Approve", f"approve:{message_id}:{chat_id}:{message_type}".encode()),
                Button.inline("🚫 Reject", f"reject:{message_id}:{chat_id}:{message_type}".encode())
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

        # Example: "approve:12345"
        action, message_id, chat_id, message_type = data.split(":")

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
        if message_type == "message":
            await event.client.delete_messages(int(chat_id), int(message_id))
        elif message_type == "album":
            await event.client.delete_messages(int(chat_id), int(message_id))
        await asyncio.sleep(2)

        # Delete message notification
        await event.delete()

    async def start(self):
        await self.client.start(bot_token=self.bot_token)
        print("Bot started successfully")

        # Register handlers
        self.client.add_event_handler(self.handle_new_message_on_source_group,
                                      events.NewMessage(chats=self.source_group))
        self.client.add_event_handler(self.handle_new_message_on_backup_group,
                                      events.NewMessage(chats=self.backup_group))
        self.client.add_event_handler(self.handle_new_album_on_backup_group, events.Album(chats=self.backup_group))
        self.client.add_event_handler(self.callback_handler)

        # Run non continuously
        await self.client.run_until_disconnected()



