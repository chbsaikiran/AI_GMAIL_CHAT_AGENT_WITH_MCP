import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import requests
import base64
import re

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/contacts.readonly"
]

def authenticate_gmail():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def get_gmail_profile():
    service = authenticate_gmail()
    creds = service._http.credentials

    response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {creds.token}"}
    )

    if response.status_code == 200:
        data = response.json()
        return {
            "email": data.get("email"),
            "first_name": data.get("given_name"),
            "last_name": data.get("family_name"),
            "full_name": data.get("name"),
        }
    else:
        raise Exception(f"Error fetching profile: {response.text}")

def fetch_emails_from_query(query: str, max_results=50):
    output = get_gmail_profile()  # Ensure authentication and get profile
    service = authenticate_gmail()
    print(f"Fetching emails with query: {query}")
    
    try:
        results = service.users().messages().list(
            userId="me", q=query, maxResults=max_results
        ).execute()
        messages = results.get("messages", [])

        snippets = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
            
            headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}
            date = headers.get('Date', '')
            subject = headers.get('Subject', '')

            # Extract the full email body (plain text or HTML)
            body = ""
            payload = msg_data.get("payload", {})
            
            if "parts" in payload:
                for part in payload["parts"]:
                    if part["mimeType"] in ["text/plain", "text/html"]:
                        data = part["body"].get("data")
                        if data:
                            body += base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            else:
                data = payload.get("body", {}).get("data")
                if data:
                    body += base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

            # Regex to find amounts like ₹123, Rs. 456, $789.00 etc.
            amounts = re.findall(r'(?:₹|Rs\.?|INR|USD|\$)\s?\d+(?:,\d{3})*(?:\.\d{1,2})?', body, re.IGNORECASE)

            snippet = msg_data.get("snippet", "")
            full_snippet = (
                f"Date: {date}\n"
                f"Subject: {subject}\n"
                f"Snippet: {snippet}\n"
                f"Amounts found: {', '.join(amounts) if amounts else 'None'}"
            )
            snippets.append(full_snippet)

        print(f"Fetched {snippets} emails for query: {query}")
        return snippets

    except Exception as e:
        print(f"Error fetching emails: {str(e)}")
        return []