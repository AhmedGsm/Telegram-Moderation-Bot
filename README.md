<div align="center">

# 🤖 Telegram Moderation Bot

### *Automate Your Group Moderation with Precision & Ease*

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Telethon](https://img.shields.io/badge/Telethon-1.34.0-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://github.com/LonamiWebs/Telethon)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-GPLv3-blue?style=for-the-badge&logo=gnu&logoColor=white)](LICENSE)

[![Status](https://img.shields.io/badge/status-stable-brightgreen?style=flat-square)](https://github.com/AhmedGsm/Telegram-Moderation-Bot)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green?style=flat-square)](https://github.com/AhmedGsm/Telegram-Moderation-Bot/graphs/commit-activity)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](http://makeapullrequest.com)

*A complete solution for Telegram group moderation with inline admin actions, user management, and a beautiful web interface.*

</div>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🎯 Use Cases](#-use-cases)
- [📸 Screenshots](#-screenshots)
- [🚀 Quick Start](#-quick-start)
- [🛠️ Installation](#️-installation)
- [⚙️ Configuration](#️-configuration)
- [💡 How It Works](#-how-it-works)
- [📊 Database Schema](#-database-schema)
- [🔧 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [👨‍💻 Author](#-author)

---

## ✨ Features

### 🔒 Content Moderation
| Feature | Description |
|---------|-------------|
| **Auto-forwarding** | Automatically forwards messages & albums to moderation group |
| **Inline Actions** | Approve/Reject with interactive buttons |
| **Smart Detection** | Detects albums vs single messages |
| **Instant Notifications** | Users receive real-time feedback |
| **Trusted Users** | Bypass moderation for verified members |

### 👥 User Management
| Action | Effect | Notification |
|--------|--------|--------------|
| ⚠️ **Warn** | Sends warning message | Custom warning text |
| 🔇 **Mute** | Temporarily blocks messaging | Mute duration notice |
| 👢 **Kick** | Removes from group | Can rejoin via link |
| 🚫 **Ban** | Permanent removal | Cannot rejoin |
| 🎖️ **Trust** | Bypasses moderation | Trusted status granted |

### 📊 User Statistics
✅ approved_posts | ❌ rejected_posts | ⚠️ warn_count
👢 kick_count | 🔇 mute_count | 🚫 ban_count

text

### 🎨 Web Interface
- **One-click setup** - No coding required
- **Group discovery** - Auto-detects your groups
- **Responsive design** - Works on all devices
- **Real-time status** - Bot running indicator

---

## 🎯 Use Cases

### Perfect For:
- 🏢 **Large Communities** - Manage thousands of members efficiently
- 📢 **Announcement Groups** - Filter spam before publication
- 👨‍👩‍👧‍👦 **Family Groups** - Keep conversations clean
- 💼 **Business Channels** - Moderate customer inquiries
- 🎓 **Educational Groups** - Prevent off-topic discussions

---

## 📸 Screenshots

<div align="center">

### Web Setup Interface
![Web Setup](https://via.placeholder.com/800x400?text=Web+Setup+Interface)

### Moderation Panel
![Moderation](https://via.placeholder.com/800x400?text=Moderation+Panel)

### User Notifications
![Notifications](https://via.placeholder.com/800x400?text=User+Notifications)

</div>

---

## 🚀 Quick Start

bash
# Clone the repository
git clone https://github.com/AhmedGsm/Telegram-Moderation-Bot.git
cd Telegram-Moderation-Bot

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py

# Open browser to http://localhost:5000
# Follow the setup wizard
# Click "Run Bot" when done!
Time to complete: ~5 minutes ⏱️

🛠️ Installation
Prerequisites
Requirement	How to Get
Python 3.8+	python.org
Telegram API ID & Hash	my.telegram.org
Bot Token	@BotFather
Telegram Account	telegram.org
Step-by-Step Installation
1️⃣ Get Telegram Credentials
bash
# Visit https://my.telegram.org
# Login with your phone number
# Create an application
# Copy API ID and API Hash
2️⃣ Create a Bot
bash
# Open Telegram and search for @BotFather
# Send: /newbot
# Choose a name (e.g., My Moderation Bot)
# Choose a username (e.g., my_moderation_bot)
# Copy the Bot Token
3️⃣ Install the Bot
bash
# Clone repository
git clone https://github.com/AhmedGsm/Telegram-Moderation-Bot.git
cd Telegram-Moderation-Bot

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py
4️⃣ Web Setup
Open http://localhost:5000

Enter your credentials:

Telegram ID (your user ID)

API ID & Hash

Bot Token

Phone number

Click "List Groups IDs"

Enter verification code (sent to Telegram)

Select Source Group & Moderation Group

Click "Register"

Click "Run Bot"

⚙️ Configuration
Environment Variables (Optional)
Create .env file:

env
TELEGRAM_API_ID=1234567
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_BOT_TOKEN=your_bot_token
SOURCE_GROUP=-1001234567890
BACKUP_GROUP=-1009876543210
ADMIN_SENDER_ID=123456789
Configuration File
The bot stores config in config/config.b64 (base64 encoded):

json
{
  "ADMIN_SENDER_ID": 123456789,
  "TELEGRAM_API_ID": 1234567,
  "TELEGRAM_API_HASH": "abc123...",
  "TELEGRAM_BOT_TOKEN": "bot_token_here",
  "SOURCE_GROUP": -1001234567890,
  "BACKUP_GROUP": -1009876543210,
  "PHONE": 1234567890
}
💡 How It Works
Architecture Diagram
text
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   User      │────▶│  Source      │────▶│  Moderation     │
│   Posts     │     │  Group       │     │  Group          │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │                       │
                           ▼                       ▼
                    ┌──────────────┐     ┌─────────────────┐
                    │   Bot        │     │  Admin Actions  │
                    │ Intercepts   │     │  • Approve      │
                    │ Message      │     │  • Reject       │
                    └──────────────┘     │  • Warn        │
                           │              │  • Mute        │
                           ▼              │  • Kick        │
                    ┌──────────────┐     │  • Ban         │
                    │  Trusted?    │     │  • Trust       │
                    └──────────────┘     └─────────────────┘
                           │                       │
                    ┌──────┴──────┐                │
                    ▼             ▼                ▼
            ┌───────────┐  ┌───────────┐   ┌─────────────┐
            │  Yes      │  │  No       │   │  Action     │
            │  Direct   │  │  Forward  │   │  Applied    │
            │  Publish  │  │  to       │   │  & User     │
            │           │  │  Mod      │   │  Notified   │
            └───────────┘  └───────────┘   └─────────────┘
Workflow Steps
User posts in source group

Bot checks if user is trusted/admin

Message forwarded to moderation group

Admins see inline action buttons

Admin chooses action (approve/reject/warn/etc.)

Bot applies action and notifies user

Statistics updated in database

📊 Database Schema
Users Table
Column	Type	Description
id	INTEGER	Telegram User ID (Primary Key)
username	TEXT	@username
first_name	TEXT	User's first name
last_name	TEXT	User's last name
phone	TEXT	Phone number
trust	TEXT	'trusted' or 'limited'
approved_posts	INTEGER	Count of approved posts
rejected_posts	INTEGER	Count of rejected posts
warn_count	INTEGER	Number of warnings
kick_count	INTEGER	Times kicked
mute_count	INTEGER	Times muted
ban_count	INTEGER	Times banned
actual_state	TEXT	Current state (active/muted/banned/kicked)
last_seen	TIMESTAMP	Last activity
🔧 Troubleshooting
Common Issues & Solutions
Issue	Solution
Bot not starting	Check if config/config.b64 exists. Run setup again.
Messages not forwarding	Ensure bot is admin in both groups
Authentication failed	Use Personal Access Token instead of password
Album detection not working	Check SINGLE_MESSAGE_DETECTION_TIMEOUT value
Database locked	Stop bot, delete database.db, restart
Logs
Logs are stored in bot.log:

bash
# View logs
tail -f bot.log

# On Windows
Get-Content bot.log -Wait
Debug Mode
python
# In setup.py
app.run(debug=True)  # Enable debug mode
🤝 Contributing
Contributions are welcome! Please follow these steps:

Fork the repository

Create a feature branch: git checkout -b feature/amazing-feature

Commit changes: git commit -m 'Add amazing feature'

Push to branch: git push origin feature/amazing-feature

Open a Pull Request

Development Setup
bash
# Clone your fork
git clone https://github.com/yourusername/Telegram-Moderation-Bot.git

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/
📄 License
text
GNU General Public License v3.0
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

You may NOT sell this software or any derivative works.

See the LICENSE file for details.

👨‍💻 Author
Ahmed Gsm
https://img.shields.io/badge/GitHub-AhmedGsm-181717?style=flat-square&logo=github
https://img.shields.io/badge/LinkedIn-Ahmed_Gsm-0077B5?style=flat-square&logo=linkedin
https://img.shields.io/badge/Upwork-Ahmed_Gsm-6fda44?style=flat-square&logo=upwork
https://img.shields.io/badge/Telegram-@AhmedGsm-2CA5E0?style=flat-square&logo=telegram

Skills Demonstrated:

🐍 Python Async Programming (asyncio)

🤖 Telegram Bot Development (Telethon)

🌐 Web Development (Flask, HTML5, CSS3, JavaScript)

🗄️ Database Design (SQLite)

🔌 API Integration

🎨 UI/UX Design

📐 System Architecture

📝 Technical Documentation

⭐ Show Your Support
If this project helped you, please give it a ⭐ on GitHub!

https://img.shields.io/github/stars/AhmedGsm/Telegram-Moderation-Bot?style=social

<div align="center">
Built with ❤️ for the Telegram Community

Questions? Issues? Open an issue on GitHub!

</div> ```
