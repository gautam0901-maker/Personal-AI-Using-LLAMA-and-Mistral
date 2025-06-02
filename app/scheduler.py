from plyer import notification
import json
import os
import threading
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import toml
from twilio.rest import Client

REMINDER_FILE = "data/reminders.json"
CONFIG_FILE = "config/secrets.toml"

def load_reminders():
    if not os.path.exists(REMINDER_FILE):
        return []
    with open(REMINDER_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_reminders(reminders):
    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f, indent=2)

def add_reminder(task, time_str):
    reminders = load_reminders()
    reminders.append({"task": task, "time": time_str, "notified": False})
    save_reminders(reminders)

# New: Delete a reminder by task
def delete_reminder(task):
    reminders = [r for r in load_reminders() if r["task"].lower() != task.lower()]
    save_reminders(reminders)

# New: Edit a reminder
def edit_reminder(old_task, new_task, new_time):
    reminders = load_reminders()
    for r in reminders:
        if r["task"].lower() == old_task.lower():
            r["task"] = new_task
            r["time"] = new_time
            r["notified"] = False
            break
    save_reminders(reminders)

def send_email(subject, body):
    config = toml.load(CONFIG_FILE)["gmail"]
    sender = config["sender"]
    password = config["password"]
    receiver = config["receiver"]

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
    except Exception as e:
        print("Error sending email:", e)

def check_reminders():
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        reminders = load_reminders()
        for reminder in reminders:
            if reminder["time"] == now and not reminder.get("notified", False):
                send_email("Pekko Reminder", f"🔔 Reminder: {reminder['task']}")
                send_sms(f"🔔 Reminder: {reminder['task']}")
                notification.notify(
                    title="Pekko Reminder",
                    message=reminder["task"],
                    app_name="Pekko",
                    timeout=10
                )
                reminder["notified"] = True
        save_reminders(reminders)
        time.sleep(60)  # check every 60 seconds

# Twilio SMS support
def send_sms(body):
    config = toml.load(CONFIG_FILE)["twilio"]
    client = Client(config["account_sid"], config["auth_token"])
    client.messages.create(
        body=body,
        from_=config["from"],
        to=config["to"]
    )

def start_scheduler():
    thread = threading.Thread(target=check_reminders, daemon=True)
    thread.start()
