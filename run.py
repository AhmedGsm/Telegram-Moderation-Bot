import asyncio
import json
from manager import TelegramPostManager

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

    async def run_all():
        # Run both manager and main() concurrently
        await asyncio.gather(
            manager.start()
        )

    asyncio.run(run_all())