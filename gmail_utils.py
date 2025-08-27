import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

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

def fetch_emails_from_query(query: str, max_results=50):
    service = authenticate_gmail()
    
    try:
        # First try with the original query
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        
        # If no results and query contains date range, try with adjusted date range
        if not messages and "after:" in query and "before:" in query:
            # Modify query to ensure we include the entire day
            query = query.replace("after:", "after:").replace("before:", "before:")
        
        # Try again with potentially modified query
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        
        snippets = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            headers = {header['name']: header['value'] for header in msg_data.get('payload', {}).get('headers', [])}
            date = headers.get('Date', '')
            subject = headers.get('Subject', '')
            snippet = msg_data.get("snippet", "")
            # Include date and subject in the snippet for better context
            full_snippet = f"Date: {date}\nSubject: {subject}\nContent: {snippet}"
            snippets.append(full_snippet)
        
        return snippets
    except Exception as e:
        print(f"Error fetching emails: {str(e)}")
        return []
