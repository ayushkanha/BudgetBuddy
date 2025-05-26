from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import base64
from email.mime.text import MIMEText
from dotenv import load_dotenv
import json
load_dotenv() 
creds_json = os.getenv("GOOGLE_CREDENTIALS")
authid = os.getenv("authid")
accountid = os.getenv("accountid")
# Gmail + Calendar scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar'
]
def get_credentials():
    creds = None

    # Read token from session or from environment
    token_str = os.getenv('GOOGLE_TOKEN_JSON')
    if token_str:
        creds = Credentials.from_authorized_user_info(json.loads(token_str), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Get credentials from environment (as string)
            client_secret_str = os.getenv("GOOGLE_CREDENTIALS")
            if not client_secret_str:
                raise ValueError("Missing GOOGLE_CREDENTIALS in environment")
            client_secret_dict = json.loads(client_secret_str)

            flow = InstalledAppFlow.from_client_config(client_secret_dict, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def send_email(to, subject, message_text):
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw_message}

    message = service.users().messages().send(userId="me", body=body).execute()
    return f"Email sent to {to}."
