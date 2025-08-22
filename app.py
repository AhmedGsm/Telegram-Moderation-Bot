from flask import Flask, render_template, request, jsonify
import json
import os
import asyncio
import threading
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
CONFIG_FILE = 'config.json'


# Create event loop for each thread
def create_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)


@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config)


@app.route('/get_groups', methods=['POST'])
def get_groups():
    try:
        api_id = request.form.get('api_id')
        api_hash = request.form.get('api_hash')
        username = request.form.get('username')
        phone = request.form.get('phone')

        if not api_id or not api_hash:
            return jsonify({'error': 'API ID and Hash are required'})

        # Create or get event loop for current thread
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = create_event_loop()
            asyncio.set_event_loop(loop)

        # Initialize client with proper session name
        session_name = username if username else 'default_session'
        client = TelegramClient(session_name, int(api_id), api_hash)

        # Start the client
        client.start(phone=phone if phone else None)

        # Get dialogs
        dialogs = client.get_dialogs()

        # Filter groups only
        groups = []
        for dialog in dialogs:
            if dialog.is_group:
                groups.append({
                    'id': dialog.id,
                    'name': dialog.name,
                })

        client.disconnect()

        return jsonify({'groups': groups})

    except SessionPasswordNeededError:
        return jsonify({'error': 'Two-factor authentication is enabled. Please provide the password.'})
    except PhoneNumberInvalidError:
        return jsonify({'error': 'The phone number is invalid.'})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/update_config', methods=['POST'])
def update_config():
    try:
        key = request.form.get('key')
        value = request.form.get('value')

        if not key or not value:
            return jsonify({'error': 'Key and value are required'})

        config = load_config()
        config[key] = value
        save_config(config)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/config')
def get_config():
    config = load_config()
    return jsonify(config)


if __name__ == '__main__':
    app.run(debug=True, threaded=True)