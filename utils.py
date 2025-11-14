import asyncio
import hashlib

class Utils:
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
            except:
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
                print("[NotifyUser] Notification deleted.")
            except Exception as e:
                print(f"[NotifyUser] Couldn't delete notification: {e}")

        except Exception as e:
            print(f"[NotifyUser] Error when sending notification: {e}")

    @staticmethod
    def hash_session_name(admin_id, prefix):
        return "_".join([prefix,
                         hashlib.md5(str(admin_id).encode()).hexdigest()])

