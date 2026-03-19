import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

ACCOUNTS_FILE = "youtube_accounts.json"
TOKENS_DIR = "tokens"

os.makedirs(TOKENS_DIR, exist_ok=True)


def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    with open(ACCOUNTS_FILE, "r") as f:
        return json.load(f)


def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=2)


def add_youtube_account():
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",
        SCOPES
    )
    creds = flow.run_local_server(port=0)

    youtube = build("youtube", "v3", credentials=creds)

    channel = youtube.channels().list(
        part="snippet",
        mine=True
    ).execute()

    items = channel.get("items", [])

    if not items:
        raise RuntimeError(
            "No YouTube channel found for this Google account.\n"
            "Please make sure:\n"
            "1. This Gmail has an active YouTube channel\n"
            "2. You are logging in with the channel OWNER email\n"
            "3. The channel is not suspended"
        )

    channel_id = items[0]["id"]
    channel_name = items[0]["snippet"]["title"]

    token_path = os.path.join(TOKENS_DIR, f"{channel_id}.json")
    if not os.path.exists(token_path):
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    accounts = load_accounts()

    # prevent duplicate accounts
    for acc in accounts:
        if acc["channel_id"] == channel_id:
            return acc

    account = {
        "channel_id": channel_id,
        "name": channel_name,
        "token_path": token_path
    }

    accounts.append(account)
    save_accounts(accounts)

    return account
