import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import requests
import base64
import re

import google.generativeai as genai
from dotenv import load_dotenv

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
def get_details_from_email_body(email_body,user_query):
    model = genai.GenerativeModel("gemini-2.0-flash")
    final_prompt = f"""Your task is to extract the following details from the email body based on the user's query:
    {user_query}
1. Amounts: Look for monetary amounts in various formats (e.g., ₹123,
    Rs. 456, $789.00, etc.) and list them.
2. Dates: Identify any dates mentioned in the email body in various formats
    (e.g., DD/MM/YYYY, MM-DD-YYYY, Month Day, Year, etc.) and list them.
3. Keywords: Extract keywords related to expenses, orders, transactions,
    bookings, payments, refunds, cancellation etc. List all relevant keywords found in the email body.
4. Summary: Provide a brief summary of the email content in one or two sentences. and definetely include the information if the ticket was cancelled or not
5. If the amounts in not in float or integer format then ignore that amount
6. If no details found then return None for that field
Only provide the extracted information in a structured format as shown below.
If any of the details are not found, indicate "None" for that field.
Format:
Amounts: [list of amounts or "None"]
Dates: [list of dates or "None"]
Keywords: [list of keywords or "None"]
Summary: [brief summary or "None"]
Email Body: {email_body}
Extracted Details:"""
    response = model.generate_content(final_prompt)
    return response.text.strip().strip('"')

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

def fetch_emails_from_query(query: str, user_query: str, max_results=50):
    #output = get_gmail_profile()  # Ensure authentication and get profile
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
            #amounts = re.findall(r'(?:₹|Rs\.?|INR|USD|\$)\s?\d+(?:,\d{3})*(?:\.\d{1,2})?', body, re.IGNORECASE)
            details = get_details_from_email_body(body,user_query)

            snippet = details
            full_snippet = (
                f"Date: {date}\n"
                f"Subject: {subject}\n"
                f"Snippet: {snippet}\n"
            )
            snippets.append(full_snippet)

        print(f"Fetched {snippets} emails for query: {query}")
        return snippets

    except Exception as e:
        print(f"Error fetching emails: {str(e)}")
        return []