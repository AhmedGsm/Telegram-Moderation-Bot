import asyncio

from flask import session

from constants import CONFIG_FILE_NOT_FOUND, CREATE_MANAGER_ERROR
from manager import TelegramPostManager
from utils import Utils


def create_manager():
    # Read config file
    try:
        config = Utils.decode_config()
    except FileNotFoundError as e:
        Utils.create_logger().error(f"{CONFIG_FILE_NOT_FOUND}: {e}")
        return
    except Exception as e:
        Utils.create_logger().error(f"{CREATE_MANAGER_ERROR}: {e}")
        return

    # Create Manager Instance
    return TelegramPostManager(
        api_id=config["TELEGRAM_API_ID"],
        api_hash=config["TELEGRAM_API_HASH"],
        bot_token=config["TELEGRAM_BOT_TOKEN"],
        source_group=config["SOURCE_GROUP"],
        backup_group=config["BACKUP_GROUP"],
        admin_id=config["ADMIN_SENDER_ID"]
    )


if __name__ == "__main__":

    # Read and decode config file
    manager = create_manager()
    async def run_all():
        # Run both manager and main() concurrently
        se = session
        if manager:
            await asyncio.gather(
                manager.start()
            )

    asyncio.run(run_all())
