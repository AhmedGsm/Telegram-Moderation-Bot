"""Global constants and user-facing messages used across the bot.

This module centralizes notification texts, delays, timeouts, and error messages
to avoid hard-coded values across the codebase."""

NOTIFICATION_HIDE_FOR_MODERATION = "The post will be reviewed, please wait. Thank you."
NOTIFICATION_NO_MORE_TEN_IMAGES = " Uploading more than 10 images is not allowed"
NOTIFICATION_NO_DIRECT_POSTING_IN_BACKUP_GROUP = " Posting in this group is not allowed!"
DELETE_NOTIFICATION_DELAY = 6
SINGLE_MESSAGE_DETECTION_TIMEOUT = 0.2
FOOTER_MODERATION_MESSAGE = """🛂 <b>Moderation Required</b>\n
This post has been forwarded to the moderation group.
Please choose an action below:
🟢 Approve, 🔴 Reject
<b>\nUser's posts counter:\n</b>"""

WARNING_MESSAGE = (
                    f"⚠ <b>Warning from the admins:</b>\n\n"
                    "You have received this warning because you shared a message "
                    "that does not respect the rules of the group "
                    "(for example: spam, advertising, offensive language, or inappropriate media).\n\n"
                    "Please make sure your next messages follow the rules. "
                    "Repeated violations may lead to a mute, kick, or ban."
                )

MUTE_MESSAGE = (
    f"🔇 <b>You have been muted by the admins</b>\n\n"
    "Your recent message violated the group rules "
    "(for example: spam, advertising, offensive language, or inappropriate media).\n\n"
    "As a result, you have been temporarily muted and cannot send messages for a limited time.\n\n"
    "Please review the group rules and make sure your future messages comply. "
    "Further violations may result in a kick or permanent ban."
)

KICK_MESSAGE = (
    f" <b>You have been temporarily removed from the group:</b> \n\n"
    "This action was taken because one of your recent messages did not follow the rules of the group.\n\n"
    "Examples of violations include:\n"
    "• Spam or repeated messages\n"
    "• Advertising or unwanted promotions\n"
    "• Offensive or inappropriate language\n"
    "• Sharing media that violates the group guidelines\n\n"
    "<b>Important:</b>\n"
    "A kick is not a ban. You can rejoin the group at any time using the group invitation link.\n\n"
    "Please make sure to respect the rules to avoid further actions such as mute or ban.\n\n"
    "Thank you for your understanding."
)

BAN_MESSAGE = (
    f"⛔ <b>You have been banned from the group:</b> \n\n"
    "This action was taken because your recent activity violated the rules of the group.\n\n"
    "Common reasons for bans include:\n"
    "• Repeated spam or disruptive behavior\n"
    "• Sharing illegal, explicit, or harmful content\n"
    "• Insulting or harassing other members\n"
    "• Ignoring multiple warnings from the moderation team\n\n"
    "<b>Important:</b>\n"
    "This ban is permanent unless the administrators decide otherwise.\n"
    "You will no longer be able to view or participate in the group.\n\n"
    "If you believe this was a mistake, you may contact the group admins privately "
    "— but please remain respectful.\n\n"
    "Thank you for your understanding."
)

TRUSTED_USER_MESSAGE = (
    "✅ <b>You are now a trusted user</b>\n\n"
    "Your message has been published directly without moderation.\n\n"
    "You are allowed to share messages and post content without prior verification or approval by the admins.\n\n"
    "Please continue to respect the group rules. "
    "Any future violations may result in the removal of your trusted status."
)

# Manager.py
NOTIFICATION_POST_APPROVED_SUCCESSFULLY = "Post has been approved successfully."
ITEM_REJECTED = "The item will not be published."
POST_REJECTED_MESSAGE = "Your post is rejected by the admins. Please follow group rules."
USER_TRUSTED_MESSAGE = "User is now trusted and can post without verification."
DM_WARNING = "DM Warning has been sent to user."
USER_KICKED = "User has been kicked."
USER_MUTED = "User has been muted."
USER_BANNED = "User has been banned."

# Setup.py
BOT_INSTALLED_SUCCESSFULLY = f"Congratulations! Your bot was installed successfully. "\
                             "You can now run it by clicking the above button!"
TG_VERIFICATION_CODE_SENT = "Verification code sent to your Telegram account. Please enter it above."
TWO_FA_AUTHENTICATION_ENABLED = "Two-factor authentication is enabled. Please enter your password."
PHONE_NUMBER_INVALID = "The phone number is invalid. Please check it and try again."
INVALID_VERIFICATION_CODE = "Invalid verification code. Please try again."
VERIFICATION_CODE_EXPIRED = "Verification code has expired. Please request a new code."
TWO_FACTOR_ENABLED = "Two-factor authentication is enabled. Please provide your password."
UNEXPECTED_ERROR_OCCURRED = "An unexpected error occurred:"
INCORRECT_PASSWORD = "Incorrect password. Please try again."
MODERATION_IS_RUNNING = "Bot is running and moderation has started..."
CONFIG_FILE_NOT_FOUND = "Please reinstall your bot."
CREATE_MANAGER_ERROR = "Error creating manager."
BOT_ALREADY_INSTALLED = "The bot is already installed. To reinstall, delete the file 'config/config.b64' and relaunch the setup."


# Error messages
ERROR_START_CLIENT = "manager.py on line 377: Error starting the client:"
ERROR_PROCESSING_MESSAGE = "moderator.py on line 78: Error processing message:"
FAILED_KICK_USER = "Failed to kick user."
NOT_MESSAGE_ALBUM = "The message type is not a message neither an album"
DELETE_NOTIFICATION_ERROR_01 = "utils.py on line 47: Couldn't delete notification:"
DELETE_NOTIFICATION_ERROR_02 = "utils.py on line 50: Couldn't delete notification:"
DELETE_SESSION_ERROR = "Utils.py on line 44: Error deleting session files"
BOT_RUNNING = "Bot is already running"
BOT_STOPPED = "Bot is stopped"

# Files
CONFIG_FILE = "config/config.b64"
PID_FILE = "bot.pid"
