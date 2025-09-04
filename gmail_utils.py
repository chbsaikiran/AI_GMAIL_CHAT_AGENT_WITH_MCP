import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import requests
import base64
import re
import asyncio
import websockets

import google.generativeai as genai
from dotenv import load_dotenv

import json
import requests

url = 'http://127.0.0.1:8005/model'

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
#client = genai.Client(api_key=api_key)
genai.configure(api_key=api_key)

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

def get_subject_and_snippet(message):
    headers = message["payload"]["headers"]
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
    snippet = message.get("snippet", "")
    return subject.lower(), snippet.lower()

def is_promotional(subject, snippet):
    PROMO_REGEX = re.compile(
    r"(offer|sale|discount|deal|limited time|hurry|coupon|save|cashback|subscribe|exclusive|get \d+% off)",
    re.IGNORECASE
)
    text = subject + " " + snippet
    return bool(PROMO_REGEX.search(text))

async def fetch_emails_from_query(max_results=20):
    async with websockets.connect("ws://ec2-13-126-198-84.ap-south-1.compute.amazonaws.com:8765/ws",ping_timeout=None) as websocket:
        await websocket.send("how much did I spent on zomato this year")
        query = await websocket.recv()
        print("Server:", query)

        # Send message to server
        #await websocket.send("Hello from client!")
        service = authenticate_gmail()
        print(f"Fetching emails with query: {query}")

        try:
            # Initial request
            results = service.users().messages().list(
                userId="me", q=query, maxResults=1
            ).execute()

            messages = results.get("messages", [])
            next_page_token = results.get("nextPageToken")

            collected_snippets = []
            total_checked = 0
            total_nonpromo = 0

            while messages and total_nonpromo < max_results:
                for msg in messages:
                    total_checked += 1

                    # Fetch full message
                    msg_data = service.users().messages().get(
                        userId="me", id=msg["id"], format="full"
                    ).execute()

                    headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}
                    date = headers.get('Date', '')
                    subject = headers.get('Subject', '')
                    snippet_preview = msg_data.get("snippet", "")

                    # Check promotion filter
                    if is_promotional(subject, snippet_preview):
                        print(f"[{total_checked}] Skipping promotional mail: {subject}")
                        continue

                    total_nonpromo += 1
                    print(f"[{total_checked}] Keeping genuine mail: {subject}")

                    # Extract email body
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

                    # Extract structured details from email body
                    await websocket.send(date)
                    await websocket.send(subject)
                    await websocket.send(body)
                    #details = get_details_from_email_body(body, user_query)

                    if total_checked >= max_results:
                        break

                # Get next page if available
                if total_checked < max_results and next_page_token:
                    results = service.users().messages().list(
                        userId="me", q=query, maxResults=1, pageToken=next_page_token
                    ).execute()
                    messages = results.get("messages", [])
                    next_page_token = results.get("nextPageToken")
                else:
                    break

            print(f"✅ Processed {total_checked} emails, kept {total_nonpromo} genuine ones.")
            #print(collected_snippets)
            await websocket.send("Done")
            #await websocket.send(collected_snippets)
            answer = await websocket.recv()
            print("Server:", answer)

        except Exception as e:
            print(f"Error fetching emails: {str(e)}")
        return []
    
asyncio.run(fetch_emails_from_query())