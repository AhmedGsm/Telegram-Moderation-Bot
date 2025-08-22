# app.py
from flask import Flask, render_template, request, jsonify, session
import json
import os
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError
import asyncio

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Ensure the config directory exists
os.makedirs('config', exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/save_config', methods=['POST'])
def save_config():
    try:
        data = request.json
        config = {
            "ADMIN_SENDER_ID": int(data['user_id']),
            "TELEGRAM_API_ID": int(data['api_id']),
            "TELEGRAM_API_HASH": data['api_hash'],
            "TELEGRAM_BOT_TOKEN": data['bot_token'],
            "SOURCE_GROUP": int(data['source_group']),
            "BACKUP_GROUP": int(data['backup_group'])
        }

        with open('config/config.json', 'w') as f:
            json.dump(config, f, indent=4)

        return jsonify({'status': 'success', 'message': 'Configuration saved successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/get_groups', methods=['POST'])
def get_groups():
    try:
        data = request.json
        api_id = int(data['api_id'])
        api_hash = data['api_hash']
        username = data['username']
        phone = data['phone']

        # Store in session for potential code verification
        session['api_id'] = api_id
        session['api_hash'] = api_hash
        session['username'] = username
        session['phone'] = phone

        # Run the Telethon code in an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        groups = []
        with TelegramClient(username, api_id, api_hash) as client:
            # Check if we need to sign in
            if not client.is_connected():
                client.connect()

            if not client.is_user_authorized():
                # Send code request
                client.send_code_request(phone)
                session['client'] = client.session.save()
                return jsonify({
                    'status': 'code_required',
                    'message': 'Verification code sent to your Telegram account. Please enter it below.'
                })

            # Get all dialogs
            dialogs = client.get_dialogs()
            for dialog in dialogs:
                if dialog.is_group or dialog.is_channel:
                    groups.append({
                        'name': dialog.name,
                        'id': dialog.id,
                        'type': 'Channel' if dialog.is_channel else 'Group'
                    })

        return jsonify({'status': 'success', 'groups': groups})

    except SessionPasswordNeededError:
        return jsonify({
            'status': 'password_required',
            'message': 'Two-factor authentication is enabled. Please enter your password.'
        })
    except PhoneNumberInvalidError:
        return jsonify({
            'status': 'error',
            'message': 'The phone number is invalid. Please check it and try again.'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/verify_code', methods=['POST'])
def verify_code():
    try:
        data = request.json
        code = data['code']

        # Recreate client from session
        client = TelegramClient(
            session=session['username'],
            api_id=session['api_id'],
            api_hash=session['api_hash']
        )

        client.connect()

        # Sign in with the code
        client.sign_in(phone=session['phone'], code=code)

        # Get all dialogs
        groups = []
        dialogs = client.get_dialogs()
        for dialog in dialogs:
            if dialog.is_group or dialog.is_channel:
                groups.append({
                    'name': dialog.name,
                    'id': dialog.id,
                    'type': 'Channel' if dialog.is_channel else 'Group'
                })

        client.disconnect()
        return jsonify({'status': 'success', 'groups': groups})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/verify_password', methods=['POST'])
def verify_password():
    try:
        data = request.json
        password = data['password']

        # Recreate client from session
        client = TelegramClient(
            session=session['username'],
            api_id=session['api_id'],
            api_hash=session['api_hash']
        )

        client.connect()

        # Sign in with the password
        client.sign_in(password=password)

        # Get all dialogs
        groups = []
        dialogs = client.get_dialogs()
        for dialog in dialogs:
            if dialog.is_group or dialog.is_channel:
                groups.append({
                    'name': dialog.name,
                    'id': dialog.id,
                    'type': 'Channel' if dialog.is_channel else 'Group'
                })

        client.disconnect()
        return jsonify({'status': 'success', 'groups': groups})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    app.run(debug=True)