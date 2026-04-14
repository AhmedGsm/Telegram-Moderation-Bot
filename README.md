# 🤖 Telegram Moderation & Backup Bot

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Telethon](https://img.shields.io/badge/Telethon-1.34.0-green.svg)](https://docs.telethon.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Automate group moderation with a powerful web dashboard.** Intercept posts, forward to a private moderation queue, and give admins one-click inline controls to approve, reject, warn, mute, kick, ban, or trust users — all in real-time.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎛️ **Inline Admin Queue** | One-click buttons: `✅ Approve` • `🚫 Reject` • `⚠ Warn` • `🔇 Mute` • `👢 Kick` • `🚫 Ban` • `🎖 Trust` |
| 📊 **User Analytics** | Tracks per-user stats: approved/rejected posts, warnings, kicks, mutes, and bans |
| 🖼️ **Atomic Album Handling** | Detects multi-image/video albums and forwards/moderates them as a single unit |
| 🔐 **Secure Web Setup** | Flask dashboard with Telegram login, 5-digit code verification, and 2FA support |
| 🛡️ **Trust System** | Trusted users bypass moderation entirely for seamless posting |
| ⚡ **Async & Lightweight** | Powered by `asyncio` + `Telethon` for concurrent, low-latency message processing |
| 📦 **Process Management** | PID tracking, graceful `SIGTERM`/`SIGINT` handling, automatic session cleanup |
| 🌐 **Responsive UI** | Modern Jinja2 templates with vanilla JS, smooth transitions, mobile-ready design |

---

## 🏗️ Architecture & Workflow

```
┌─────────────────────────────────────┐
│  User posts in Source Group         │
└─────────────┬───────────────────────┘
              ▼
┌─────────────────────────────────────┐
│  [ContentModerator] intercepts      │
│  • Hides original post              │
│  • Forwards to Backup Group         │
│  • Sends temp notification:         │
│    "The post will be reviewed..."   │
└─────────────┬───────────────────────┘
              ▼
┌─────────────────────────────────────┐
│  Admin sees post + inline buttons   │
│  in Backup/Moderation Group         │
│                                     │
│  [✅ Approve] [🚫 Reject]          │
│  [⚠ Warn] [🔇 Mute] [👢 Kick]     │
│  [🚫 Ban] [🎖 Trust User]          │
└─────────────┬───────────────────────┘
              ▼
┌─────────────────────────────────────┐
│  Admin clicks action →              │
│  [TelegramPostManager] executes:    │
│                                     │
│  • Approve → forwards back          │
│  • Reject → deletes + DMs user      │
│  • Warn/Mute/Kick/Ban → applies     │
│    restriction + logs to DB + DMs   │
│  • Trust → flags user → bypasses    │
│    future moderation                │
└─────────────┬───────────────────────┘
              ▼
┌─────────────────────────────────────┐
│  Notification auto-deletes after 2s │
│  User stats updated in userdb       │
└─────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Python 3.9+, Flask 3.0, Telethon 1.34, `asyncio` |
| **Frontend** | Jinja2, HTML5, CSS3, Vanilla JavaScript (ES6+) |
| **Data/Config** | Base64-encoded config (`config/config.b64`), lightweight user DB (`userdb.py`), PID tracking (`bot.pid`) |
| **Auth** | Telegram MTProto, SMS/Call verification, 2FA password flow |
| **Utilities** | `psutil` for process monitoring, `python-dotenv` for environment management |

---

## 📦 Installation & Setup

### 1️⃣ Prerequisites
- Python `3.9` or higher
- Telegram API credentials from [my.telegram.org](https://my.telegram.org/) (`API_ID`, `API_HASH`)
- A Telegram Bot token from [@BotFather](https://t.me/BotFather)
- Admin rights in both the **Source** and **Backup/Moderation** groups

### 2️⃣ Quick Start
```bash
# Clone repository
git clone https://github.com/yourusername/telegram-moderation-bot.git
cd telegram-moderation-bot

# Create & activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask web dashboard
flask run --app=run.py --port=5000
```

### 3️⃣ Web Setup Wizard
1. Navigate to `http://localhost:5000/setup`
2. Enter your credentials:
   - `Telegram API ID` & `API Hash`
   - `Bot Token`
   - `Phone Number` (with country code)
3. Enter the **5-digit verification code** sent to your Telegram
4. If 2FA is enabled, enter your cloud password
5. Click **"List Groups"** to fetch your accessible chats
6. Select your **Main Group** and **Moderation Group**
7. Click **"Register"** to save configuration (`config/config.b64`)
8. Go to `/run` and click **"Run Bot"** to start moderation

> 💡 **Tip:** Keep the Flask server running in the background (use `nohup`, `screen`, or a process manager like `pm2` or `systemd` for production).

---

## 📁 Project Structure

```
telegram-moderation-bot/
├── constants.py          # Centralized messages, timeouts & paths
├── manager.py            # Core workflow, Telethon event routing & inline actions
├── moderator.py          # Per-user moderation logic & album detection
├── run.py                # Bot process entry, config loader & signal handling
├── userdb.py             # Lightweight user stats & trust database
├── utils.py              # Helpers: config encoding/decoding, logging, notifications
├── requirements.txt      # Python dependencies
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Master layout with navigation
│   ├── setup.html        # Credentials form + verification flow
│   ├── run.html          # One-click bot start page
│   ├── features.html     # Feature showcase
│   └── no-setup.html     # Redirect when config missing
└── static/               # Frontend assets
    ├── bot.css           # Dashboard styling (gradients, animations)
    ├── ignore.css        # Global resets, variables, responsive utilities
    ├── script.js         # UI behavior: sidebar toggle, responsive handling
    ├── setup.js          # Setup wizard: form validation, Telegram auth, group fetch
    └── bot.js            # Bot runner: safeFetch wrapper, feedback handling
```

---

## ⚙️ Configuration Reference

### Environment Variables (Optional)
Create a `.env` file for sensitive values:
```env
FLASK_ENV=production
FLASK_DEBUG=0
```

### Key Constants (`constants.py`)
| Constant | Default | Purpose |
|----------|---------|---------|
| `DELETE_NOTIFICATION_DELAY` | `6` (seconds) | Auto-delete temp moderation notifications |
| `SINGLE_MESSAGE_DETECTION_TIMEOUT` | `0.2` (seconds) | Threshold to detect album vs. single message |
| `CONFIG_FILE` | `"config/config.b64"` | Encoded storage for credentials & group IDs |
| `PID_FILE` | `"bot.pid"` | Track running bot process for graceful shutdown |

### User Database Schema (`userdb.py`)
Each user entry tracks:
```json
{
  "user_id": 123456789,
  "approved_posts": 42,
  "rejected_posts": 3,
  "warn_count": 1,
  "kick_count": 0,
  "mute_count": 2,
  "ban_count": 0,
  "trust": "trusted"
}
```

---

## 🚀 Usage Guide

### Admin Actions Reference
| Button | Effect |
|--------|--------|
| `✅ Approve post` | Forwards message/album back to source group; increments `approved_posts` |
| `🚫 Reject post` | Deletes post; sends DM: *"Your post is rejected by the admins"*; increments `rejected_posts` |
| `⚠ Warn user` | Sends warning DM; increments `warn_count` |
| `🔇 Mute user` | Revokes `send_messages` permission; sends mute DM; increments `mute_count` |
| `👢 Kick user` | Removes user (rejoin allowed); sends kick DM; increments `kick_count` |
| `🚫 Ban user` | Revokes `view_messages` permission; sends ban DM; increments `ban_count` |
| `🎖 Trust User` | Sets `trust: "trusted"`; user bypasses future moderation |

### Trust Workflow
1. Admin clicks **"Trust User"** on a moderated post
2. User is flagged in `userdb`
3. Next time the user posts: `ContentModerator` checks `db.get_user(user_id, "trust")`
4. If `"trusted"`, the post is **not intercepted** and appears normally

---

## 💡 Troubleshooting

| Issue | Solution |
|-------|----------|
| `Config not found` | Complete web setup at `/setup` or delete `config/config.b64` and restart |
| `Bot won't start` | Check if `bot.pid` exists → delete if stale, then restart Flask |
| `Albums split incorrectly` | Adjust `SINGLE_MESSAGE_DETECTION_TIMEOUT` in `constants.py` |
| `2FA loop / password rejected` | Ensure your Telegram cloud password is entered exactly |
| `Inline buttons not responding` | Verify bot is admin in **both** groups with `Delete Messages` + `Ban Users` rights |
| `Groups not loading` | Ensure `API_ID`/`API_HASH` are valid and phone number includes country code |

---

## 🔐 Security Best Practices
- ✅ Credentials are Base64-encoded in `config/config.b64` (not plaintext)
- ✅ Telethon session files (`.session`) are hashed by `admin_id` to avoid collisions
- ✅ Only the configured `admin_id` can trigger moderation actions via callback queries
- ✅ All user-facing messages use `parse_mode="html"` with sanitized content
- ✅ Process isolation via PID file prevents duplicate bot instances

> ⚠️ **Production Note:** For public deployments, add HTTPS (use `gunicorn` + `nginx`), rate-limit Flask endpoints, and store `config.b64` outside the web root.

---

## 🤝 Contributing
We welcome improvements! Please follow these steps:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-idea`
3. Make changes and test locally
4. Commit with clear messages: `git commit -m 'feat: add bulk trust import'`
5. Push and open a Pull Request

### Development Tips
- Use `flask run --debug` for auto-reload during frontend/backend changes
- Logs are written via `Utils.create_logger()` — check `logs/` directory
- Mock Telegram events using Telethon's `events.NewMessage` builder for unit tests

---

## 📄 License
Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

> 📬 **Support & Feedback**  
> Found a bug? Have a feature request?  
> → [Open an Issue](https://github.com/yourusername/telegram-moderation-bot/issues)  
> → Or reach out via Telegram for priority support.

*Built for community safety. Designed for simplicity. Powered by open source.* 🌟
