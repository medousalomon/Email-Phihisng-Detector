import re
import base64
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import streamlit as st


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def clean_html(raw_html):

    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def get_gmail_flow():

    client_config = {
        "web": {
            "client_id": st.secrets["GMAIL_CLIENT_ID"],
            "client_secret": st.secrets["GMAIL_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                st.secrets["GMAIL_REDIRECT_URI"]
            ]
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=st.secrets["GMAIL_REDIRECT_URI"],
        autogenerate_code_verifier=False
    )

    return flow


def get_gmail_auth_url():

    flow = get_gmail_flow()

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    return auth_url


def get_credentials_from_code(code):

    flow = get_gmail_flow()

    flow.fetch_token(
        code=code
    )

    return flow.credentials


def extract_email_body(payload):

    body = ""

    def walk_parts(part):

        nonlocal body

        mime_type = part.get("mimeType", "")

        data = part.get("body", {}).get("data")

        if data and mime_type in ["text/plain", "text/html"]:

            decoded = base64.urlsafe_b64decode(
                data
            ).decode(
                "utf-8",
                errors="ignore"
            )

            if mime_type == "text/html":
                decoded = clean_html(decoded)

            body += decoded + "\n"

        for sub_part in part.get("parts", []):
            walk_parts(sub_part)

    walk_parts(payload)

    return body


def fetch_recent_emails(credentials, max_results=5):

    service = build(
        "gmail",
        "v1",
        credentials=credentials
    )

    results = service.users().messages().list(
        userId="me",
        maxResults=max_results
    ).execute()

    messages = results.get(
        "messages",
        []
    )

    emails = []

    for msg in messages:

        message = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        payload = message.get("payload", {})

        headers = payload.get("headers", [])

        subject = ""

        sender = ""

        for header in headers:

            if header["name"].lower() == "subject":
                subject = header["value"]

            if header["name"].lower() == "from":
                sender = header["value"]

        body = extract_email_body(payload)

        emails.append({
            "sender": sender,
            "subject": subject,
            "body": body
        })

    return emails