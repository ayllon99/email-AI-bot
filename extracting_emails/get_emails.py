import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email import message_from_bytes
from email.utils import parsedate_to_datetime
from datetime import datetime
import pandas as pd
import json
from dotenv import load_dotenv


load_dotenv()


SCOPES = [os.getenv('SCOPES')]
TOKEN_PATH = os.getenv('TOKEN_PATH')
CREDENTIALS_PATH = os.getenv('CREDENTIALS_PATH')

def authenticate_gmail():
    creds = None
    # Load existing token if available
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    # Authenticate via browser if no valid token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the token for future runs
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_emails(service, max_results=50):
    df = pd.DataFrame()
    try:
        # Fetch list of emails
        result = service.users().messages().list(
            userId='me',
            maxResults=max_results
        ).execute()
        messages = result.get('messages', [])
        # Process each email
        for msg in messages:
            msg_data = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='raw'
            ).execute()
            
            # Decode and parse the email
            raw_msg = base64.urlsafe_b64decode(msg_data['raw'])
            email_msg = message_from_bytes(raw_msg)
            
            # Extract email details
            subject = email_msg.get('Subject', 'No Subject')
            sender = email_msg.get('From', 'Unknown Sender')
            email_from = sender.split('<')[1].replace('>','')
            date = email_msg.get('Date', 'Unknown Date')
            labels = json.dumps(msg_data['labelIds'])
            parsed_datetime = parsedate_to_datetime(date).isoformat()
            body = ""
            
            # Get plain-text body
            if email_msg.is_multipart():
                for part in email_msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = email_msg.get_payload(decode=True).decode()

            now = datetime.now().isoformat()
            msg_df = pd.DataFrame({'email_id': [msg_data['id']],
                                   'thread_id': [msg_data['threadId']],
                                   'labels': [labels],
                                   'sent_datetime': [parsed_datetime],
                                   'subject': [subject],
                                   'sender': [sender],
                                   'email_from': [email_from],
                                   'body': [body],
                                   'processed': [False],
                                   'extraction_timestamp': [now]})
            df = pd.concat([df, msg_df])
    except Exception as e:
        print(f"Error: {e}")
    return df

if __name__ == '__main__':
    service = authenticate_gmail()
    df = get_emails(service, max_results=10)
    print(df)
