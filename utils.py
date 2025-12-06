import asyncio
import hashlib
import os
import logging
import base64
import json


class Utils:
    @staticmethod
    def hash_session_name(admin_id, prefix):
        return "_".join([prefix,
                         hashlib.md5(str(admin_id).encode()).hexdigest()])

    @staticmethod
    def clear_session(admin_id, prefix, session):
        # Delete previous session file if it exists
        session_file = f"{Utils.hash_session_name(admin_id, prefix)}.session"
        if os.path.exists(session_file):
            os.remove(session_file)

        # Also delete any previous session-journal file
        session_journal_file = f"{Utils.hash_session_name(admin_id, prefix)}.session-journal"
        if os.path.exists(session_journal_file):
            os.remove(session_journal_file)

        # Clear any existing session data
        session.clear()

    @staticmethod
    def clear_all_sessions():
        # Get the current directory
        current_dir = os.getcwd()

        # Loop through files in the directory
        for file_name in os.listdir(current_dir):
            # Check if the file ends with .session or starts with session_journal
            if file_name.endswith('.session') or file_name.startswith('session_journal'):
                try:
                    # Construct full file path
                    file_path = os.path.join(current_dir, file_name)
                    # Remove the session file
                    os.remove(file_path)

                except Exception as e:
                    Utils.create_logger().error(f"{DELETE_SESSION_ERROR} {file_name}: {e}")

    @staticmethod
    async def notify_user(client, source_group, event, message, delay):
        """
        Sends a temporary notification to a user in the source group and
        deletes it after `delay` seconds.

        Parameters:
            client        → Telethon client instance
            source_group  → ID of the source group where notification is posted
            event         → Telethon event (NewMessage or Album)
            message       → Text message to notify the user with
            delay         → Time to wait before deleting the notification
        """
        try:
            # Get sender of the original message
            sender = await event.get_sender()
            username = sender.username or sender.first_name or "User"

            # Build notification text
            text = f"@{username} {message}"

            # Try retrieving the original replied message ID
            try:
                reply_to = event.message.reply_to_msg_id
            except AttributeError:
                reply_to = None

            # Send notification
            notification = await client.send_message(
                source_group,
                text,
                reply_to=reply_to
            )

            # Wait before cleanup
            await asyncio.sleep(delay)

            # Delete notification safely
            try:
                await client.delete_messages(source_group, notification.id)
            except Exception as e:
                Utils.create_logger().error(f"{DELETE_NOTIFICATION_ERROR} {e}")

        except Exception as e:
            Utils.create_logger().error(f"{DELETE_NOTIFICATION_ERROR_02} {e}")

    @staticmethod
    def create_logger():
        logging.basicConfig(
            level=logging.ERROR,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("bot.log", encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger("BotLogger")

    @staticmethod
    def encode_config(config_dict):
        json_str = json.dumps(config_dict)
        encoded = base64.b64encode(json_str.encode()).decode()
        with open('config/config.b64', 'w') as f:
            f.write(encoded)
        return encoded

    @staticmethod
    def decode_config():
        # Read encoded config
        with open('config/config.b64', 'r') as f:
            encoded = f.read()
        decoded = base64.b64decode(encoded).decode()
        return json.loads(decoded)
