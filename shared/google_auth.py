#!/usr/bin/env python3
"""
google_auth.py — Shared OAuth-based Google Sheets/Drive auth.

Authenticates as your own Google account via the OAuth installed-app flow
(no service account key needed). First run opens a browser to authorize;
after that the token refreshes itself automatically.

Setup: see README.md "Google Sheets setup" — you'll create an OAuth Desktop
client in Google Cloud Console and save its JSON as config/credentials.json.

Usage:
    from google_auth import get_gspread_client
    gc = get_gspread_client()

To force a fresh interactive authorization (e.g. if the token is revoked):
    python3 shared/google_auth.py --reauth
"""

import sys

import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from config import GOOGLE_CLIENT_SECRETS, GOOGLE_TOKEN_PATH

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _interactive_authorize() -> Credentials:
    if not GOOGLE_CLIENT_SECRETS.exists():
        raise FileNotFoundError(
            f"Google OAuth client secrets not found at {GOOGLE_CLIENT_SECRETS}. "
            f"See README.md 'Google Sheets setup' to create one."
        )
    GOOGLE_TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    flow = InstalledAppFlow.from_client_secrets_file(str(GOOGLE_CLIENT_SECRETS), SCOPES)
    creds = flow.run_local_server(port=0)
    GOOGLE_TOKEN_PATH.write_text(creds.to_json())
    return creds


def get_credentials() -> Credentials:
    if GOOGLE_TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(GOOGLE_TOKEN_PATH), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            GOOGLE_TOKEN_PATH.write_text(creds.to_json())
        return creds

    return _interactive_authorize()


def get_gspread_client() -> gspread.Client:
    return gspread.authorize(get_credentials())


if __name__ == "__main__":
    if "--reauth" in sys.argv:
        creds = _interactive_authorize()
    else:
        creds = get_credentials()
    print(f"Authorized. Token at {GOOGLE_TOKEN_PATH}")
