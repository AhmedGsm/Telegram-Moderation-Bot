# setup.py
from flask import Flask, render_template, request, jsonify, session
import json
import os
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError, PhoneCodeInvalidError, \
    PhoneCodeExpiredError, PasswordHashInvalidError
import asyncio
import secrets
import subprocess
from flask import redirect, url_for

from utils import Utils


class Setup:
    @staticmethod
    def get_or_create_secret_key():
        config_dir = 'config'
        key_file = os.path.join(config_dir, 'secret.key')
    
        # Create config directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
    
        # Generate new key if doesn't exist
        if not os.path.exists(key_file):
            secret_key = secrets.token_hex(32)
            with open(key_file, 'w') as f:
                f.write(secret_key)
            return secret_key
    
        # Read existing key
        with open(key_file, 'r') as f:
            return f.read().strip()

    @staticmethod
    def clear_session(username):
        # Delete previous session file if it exists
        session_file = f"{username}.session"
        if os.path.exists(session_file):
            os.remove(session_file)
            print(f"Deleted previous session file: {session_file}")
        # Also delete any previous session-journal file
        session_journal_file = f"{username}.session-journal"
        if os.path.exists(session_journal_file):
            os.remove(session_journal_file)
            print(f"Deleted previous session journal file: {session_journal_file}")
        # Clear any existing session data
        session.clear()

    @staticmethod
    def fetch_groups( client):
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
        #client.disconnect()
        return groups

app = Flask(__name__)
app.secret_key = Setup.get_or_create_secret_key()

@app.route('/')
def index():
    return redirect(url_for('features'))

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/setup')
def setup():
    return render_template('setup.html')


@app.route('/save_config', methods=['POST'])
def save_config():
    try:
        data = request.json
        config = {
            "ADMIN_SENDER_ID": int(data['admin_id']),
            "TELEGRAM_API_ID": int(data['api_id']),
            "TELEGRAM_API_HASH": data['api_hash'],
            "TELEGRAM_BOT_TOKEN": data['bot_token'],
            "SOURCE_GROUP": int(data['source_group']),
            "BACKUP_GROUP": int(data['backup_group']),
            "PHONE": int(data['phone'])
        }

        with open('config/config.json', 'w') as f:
            json.dump(config, f, indent=4)

        return jsonify({'status': 'success', 'message': 'Congratulations! Your bot was installed successfully. You can now run it by clicking the above button!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/setup_session', methods=['POST'])
def setup_session():

    try:
        data = request.json
        #clear_session(data['username'])

        admin_id = int(data['admin_id'])
        api_id = int(data['api_id'])
        api_hash = data['api_hash']
        phone = data['phone']

        # Store in session for potential code verification
        session['admin_id'] = str(admin_id)
        session['api_id'] = api_id
        session['api_hash'] = api_hash
        session['phone'] = phone

        # Run the Telethon code in an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        session_name = Utils.hash_session_name(admin_id, "user")
        # Save session name in a session
        session['session_name'] = session_name

        client = TelegramClient(session_name, api_id, api_hash)
        # Check if we need to sign in
        if not client.is_connected():
            client.connect()

        if not client.is_user_authorized():
            # Send code request
            result = client.send_code_request(phone)
            session['phone_code_hash'] = result.phone_code_hash

            session['client'] = client.session.save()

            # PROPERLY DISCONNECT before returning
            if client.is_connected():
                client.disconnect()

            return jsonify({
                'status': 'code_required',
                'message': 'Verification code sent to your Telegram account. Please enter it below.'
            })

        groups = Setup.fetch_groups(client)
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

    finally:
        # PROPERLY DISCONNECT before returning
        if client and client.is_connected():
            client.disconnect()


@app.route('/verify_code', methods=['POST'])
def verify_code():
    #client = None
    try:
        data = request.json
        code = data['code']

        # Run the Telethon code in an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Recreate client from session
        client = TelegramClient(session['session_name'], session['api_id'], session['api_id'])

        client.connect()

        # Sign in with the code
        client.sign_in(phone=session['phone'], code=code, phone_code_hash=session['phone_code_hash'])

        # Get all dialogs
        groups = Setup.fetch_groups(client)
        return jsonify({'status': 'success', 'groups': groups})

    except PhoneCodeInvalidError:
        return jsonify({'status': 'error', 'message': 'Invalid verification code. Please try again.'}), 400


    except PhoneCodeExpiredError:
        return jsonify({'status': 'error', 'message': 'Verification code has expired. Please request a new code.'}), 400


    except SessionPasswordNeededError:

        return jsonify(
            {'status': 'error', '2fa_required': '2fa', 'message': 'Two-factor authentication is enabled. Please provide your password.'}), 400

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}), 500

    finally:
        # PROPERLY DISCONNECT before returning
        if client and client.is_connected():
            client.disconnect()

"""
@app.route('/verify_password', methods=['POST'])
def verify_password():
    try:
        data = request.json
        password = data['password']

        # Run the Telethon code in an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Recreate client from session
        client = TelegramClient(session['session_name'], session['api_id'], session['api_id'])

        # Connect the client
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
        return jsonify({'status': 'error', 'message': str(e)})"""

@app.route('/validate_2fa', methods=['POST'])
def validate_2fa():
    try:
        data = request.json
        password = data['password']

        # Run the Telethon code in an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Recreate the client from the session
        client = TelegramClient(session['session_name'], session['api_id'], session['api_hash'])
        client.connect()

        # Try signing in using the provided password if 2FA is enabled
        client.sign_in(password=password)

        # If sign-in is successful, fetch the groups
        groups = Setup.fetch_groups(client)
        return jsonify({'status': 'success', 'groups': groups})

    except PasswordHashInvalidError:
        return jsonify({
            'status': 'error',
            'message': 'Incorrect password. Please try again.'
        }), 400

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}), 500

    finally:
        # Properly disconnect before returning
        if client and client.is_connected():
            client.disconnect()

@app.route('/run_bot', methods=['POST'])
def run_bot():
    try:
        # Launch moderator.py as a subprocess
        subprocess.Popen(["python", "moderator.py"])
        return jsonify({'status': 'success', 'message': 'Bot is running and start moderation...'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/run')
def run_page():
    # If config.json doesn’t exist, redirect to setup page
    if not os.path.exists("config/config.json"):
        return redirect(url_for('no_setup'))
    return render_template('run.html')


@app.route('/no-setup')
def no_setup():
    return render_template('no-setup.html')

if __name__ == '__main__':

    # Ensure the config directory exists
    os.makedirs('config', exist_ok=True)

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', True), use_reloader=False)