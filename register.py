from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)
CONFIG_FILE = "config.json"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Read form data from the client
        bot_token = request.form["bot_token"]
        source_group = request.form["source_group"]
        backup_group = request.form["backup_group"]
        admin_sender_id = request.form["admin_sender_id"]

        # Create a dictionary with API keys
        config_data = {
            "TELEGRAM_BOT_TOKEN": bot_token,
            "SOURCE_GROUP": int(source_group),
            "BACKUP_GROUP": int(backup_group),
            "ADMIN_SENDER_ID": int(admin_sender_id)
        }

        # Save credentials to config.json
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=4)

        return "<h3>Bot configuration saved successfully!</h3>"

    # Preload values if config.json exists
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            saved_config = json.load(f)
    else:
        saved_config = {
            "TELEGRAM_BOT_TOKEN": "",
            "SOURCE_GROUP": "",
            "BACKUP_GROUP": "",
            "ADMIN_SENDER_ID": ""
        }

    return render_template("register.html", config=saved_config)


if __name__ == "__main__":
    app.run(debug=True)
