import base64
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import streamlit as st


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


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
        redirect_uri=st.secrets["GMAIL_REDIRECT_URI"]
    )

    return flow


def get_gmail_auth_url():

    flow = get_gmail_flow()

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    st.session_state.code_verifier = flow.code_verifier

    return auth_url


def get_credentials_from_code(code):

    flow = get_gmail_flow()

    flow.code_verifier = st.session_state.code_verifier

    flow.fetch_token(
        code=code
    )

    return flow.credentials


def extract_email_body(payload):

    body = ""

    if "parts" in payload:

        for part in payload["parts"]:

            if part.get("mimeType") == "text/plain":

                data = part["body"].get("data")

                if data:

                    body += base64.urlsafe_b64decode(
                        data
                    ).decode(
                        "utf-8",
                        errors="ignore"
                    )

    else:

        data = payload.get("body", {}).get("data")

        if data:

            body = base64.urlsafe_b64decode(
                data
            ).decode(
                "utf-8",
                errors="ignore"
            )

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