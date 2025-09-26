# notifier.py (Updated with Cheeky Personality!)
import streamlit as st
import pandas as pd
from datetime import datetime
import random # We need this to pick random phrases
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# --- CONFIGURATION ---
DATA_FILE = "data/tasks.csv"
REMINDER_DAYS = [1, 3]

# --- PERSONALITY POOLS (The Fun Part!) ---

SUBJECT_LINES = [
    "Psst... Your Deadlines Are Calling!",
    "A Missive From Your Future Self 💌",
    "Operation: Get Things Done is a GO!",
    "Your Daily Dose of 'You Got This!'",
    "Beep Boop... Task Alert! 🤖",
    "An Update from Mission Control...",
]

HEADINGS = [
    "Let's Crush These, Shall We?",
    "Your Mission, Should You Choose to Accept It...",
    "The Universe (and your calendar) Demands Action!",
    "Rise and Shine! It's Productivity Time.",
    "A Peek at What's on the Horizon...",
]

SIGN_OFFS = [
    "Go get 'em, tiger!",
    "You've got this. Now go be awesome.",
    "Sent by your #1 fan, The Compass App.",
    "Over and out.",
]

# --- HELPER FUNCTIONS ---
def load_tasks():
    try:
        return pd.read_csv(DATA_FILE, parse_dates=['due_date'])
    except FileNotFoundError:
        return pd.DataFrame()

# --- THIS IS THE FULLY REVAMPED FUNCTION ---
def format_email_body(tasks_to_remind):
    """Formats the list of tasks into a fun, styled HTML email body."""
    
    # Randomly pick a heading and sign-off
    heading = random.choice(HEADINGS)
    sign_off = random.choice(SIGN_OFFS)

    # Building the task list as HTML list items
    task_list_html = ""
    for task in tasks_to_remind:
        day_str = "day" if task['days_left'] == 1 else "days"
        due_info = f"is due in <b>{task['days_left']} {day_str}</b>" if task['days_left'] != "Today" else "is <b>Due Today!</b>"
        task_list_html += f"<li>{task['task_name']} &mdash; {due_info} on {task['due_date'].strftime('%A, %b %d')}.</li>"

    # Using an f-string to build the entire HTML body with inline CSS for style
    body_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f4f7f6; color: #333; }}
            .container {{ max-width: 600px; margin: 20px auto; padding: 25px; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.07); }}
            h1 {{ color: #2c3e50; font-size: 24px; }}
            ul {{ list-style-type: none; padding: 0; }}
            li {{ background-color: #ecf0f1; margin-bottom: 10px; padding: 15px; border-radius: 8px; font-size: 16px; border-left: 5px solid #3498db; }}
            p {{ line-height: 1.6; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{heading}</h1>
            <p>Just a friendly nudge from your digital sidekick. Here’s the game plan for the next few days:</p>
            <ul>
                {task_list_html}
            </ul>
            <p>{sign_off}</p>
        </div>
    </body>
    </html>
    """
    return body_html

# The send_email and main functions are mostly the same, just with minor updates.
def send_email(subject, body_html):
    api_key = st.secrets.get("BREVO_API_KEY")
    to_email = st.secrets.get("TO_EMAIL")
    from_email = st.secrets.get("FROM_EMAIL")
    if not all([api_key, to_email, from_email]):
        print("Error: Missing secrets.")
        return
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    sender = {"email": from_email, "name": "The Compass App"}
    to = [{"email": to_email}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, sender=sender, subject=subject, html_content=body_html)
    try:
        api_instance.send_transac_email(send_smtp_email)
        print("✅ SUCCESS: Cheeky email sent successfully!")
    except ApiException as e:
        print(f"🔴 ERROR sending email: {e}")

def main():
    print("Running notifier script...")
    tasks_df = load_tasks()
    if tasks_df.empty:
        return

    active_tasks = tasks_df[tasks_df['status'] == 'Active']
    tasks_to_remind_list = []
    today = datetime.now().date()

    for index, row in active_tasks.iterrows():
        if pd.isna(row['due_date']):
            continue
        delta = row['due_date'].date() - today
        days_left = delta.days
        if days_left == 0 or days_left in REMINDER_DAYS:
            tasks_to_remind_list.append({
                'task_name': row['task_name'],
                'due_date': row['due_date'],
                'days_left': "Today" if days_left == 0 else days_left
            })
            
    if tasks_to_remind_list:
        # --- Random subject line is chosen here! ---
        subject = f"{random.choice(SUBJECT_LINES)} ({len(tasks_to_remind_list)} upcoming)"
        email_body = format_email_body(tasks_to_remind_list)
        send_email(subject, email_body)
    else:
        print("No reminders to send today.")

if __name__ == "__main__":
    main()