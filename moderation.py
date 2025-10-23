
from telethon import TelegramClient, events, Button
import json
import asyncio
class Moderator:
    def __init__(self, api_id, api_hash, bot_token, source_group, backup_group, admin_id):
        self.client = TelegramClient("session__name__", api_id, api_hash)
        self.bot_token = bot_token
        self.source_group = source_group
        self.backup_group = backup_group
        self.admin_id = admin_id
        self.message_ids_list = []

    async def start_handler(self, event):
        print("start_handler")
        print("event message ID " + str(event.message.id))
        msg = event.message
        if msg.media:
            print("Message type is a media  ")
        elif msg.message:
            print("Message type is a text  ")
        # Build message text
        await self.show_notification_menu(event)


    async def show_notification_menu(self, event):
        text = (
            "✨ <b>Welcome!</b>\n"
            "I'm alive and glowing.\n\n"
            "Choose what you want to do next 👇"
        )
        # Build inline keyboard
        keyboard = [
            [
                Button.inline("✅ Approve", f"approve:{event.message.id}:{event.message.chat_id}".encode()),
                Button.inline("🚫 Reject", f"reject:{event.message.id}:{event.message.chat_id}".encode())
            ]
        ]

        # Append message ids
        self.message_ids_list.append(event.message.id)

        # Wait until all message arrive before displaying menu notification
        await asyncio.sleep(2)
        await event.respond(
            text,
            buttons=keyboard,
            parse_mode="html"
        )


    # Handle button presses (CallbackQuery)
    @events.register(events.CallbackQuery)
    async def callback_handler(self, event):
        data = event.data.decode("utf-8")

        # Example: "approve:12345"
        action, message_id, chat_id = data.split(":")

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
        await event.client.delete_messages(int(chat_id), int(message_id))
        await asyncio.sleep(2)
        await event.delete()

    async def album_handler(self, event):
        print("album_handler Album is uploaded!")

    async def moderate(self):

        await self.client.start(bot_token=self.bot_token)

        # Register handlers
        self.client.add_event_handler(self.start_handler, events.NewMessage(chats=self.backup_group))

        # only albums from your backup group
        self.client.add_event_handler(self.album_handler, events.Album(chats=self.backup_group))
        self.client.add_event_handler(self.callback_handler)

        # Run non continuously
        await self.client.run_until_disconnected()

if __name__ == "__main__":
    # Load json file
    with open("config/config.json") as f:
        config = json.load(f)
        API_ID = config["TELEGRAM_API_ID"]
        API_HASH = config["TELEGRAM_API_HASH"]
        BOT_TOKEN = config["TELEGRAM_BOT_TOKEN"]
        SOURCE_GROUP_ID = config["SOURCE_GROUP"]
        BACKUP_GROUP_ID = config["BACKUP_GROUP"]
        ADMIN_SENDER_ID = config["ADMIN_SENDER_ID"]

        moderator = Moderator(SOURCE_GROUP_ID, BACKUP_GROUP_ID)
        asyncio.run(moderator.moderate())
