import base64
import re
from bs4 import BeautifulSoup
from gmail_connect import authenticate_gmail
from email_classifier import classify_all_email, display_classified_emails

def fetch_emails(service, max_results=10):
    """
    Fetches latest emails from inbox
    in: gmail service object, number of emails to fetch
    out: list of parsed email dictionaries
    """
    print(f"\nFetching last {max_results} emails...........")

    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
        return []

    print(f"Found {len(messages)} messages. Parsing...........")

    emails = []
    for msg in messages:
        email_data = parse_email(service, msg['id'])
        emails.append(email_data)

    return emails


def parse_email(service, msg_id):
    """
    Fetches and parses a single email by ID
    in: service object, message ID string
    out: dictionary with subject, sender, date, body
    """
    message = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='full'
    ).execute()

    headers = message['payload']['headers']

    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
    date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

    body = extract_body(message['payload'])

    return {
        'id': msg_id,
        'subject': subject,
        'sender': sender,
        'date': date,
        'body': body[:500]
    }


def extract_body(payload):
    """
    Extracts readable text from email payload
    in: message payload dict
    out: plain text string
    email has weird encoding or nested parts
    """
    plain_body = ""
    html_body = ""

    if 'parts' in payload:
        for part in payload['parts']:

            # Handle nested multipart emails
            if part['mimeType'] == 'multipart/alternative':
                for subpart in part.get('parts', []):
                    data = subpart['body'].get('data', '')
                    if not data:
                        continue
                    decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    if subpart['mimeType'] == 'text/plain':
                        plain_body = decoded
                    elif subpart['mimeType'] == 'text/html':
                        html_body = decoded

            # Direct plain text part
            elif part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    plain_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

            # Direct html part
            elif part['mimeType'] == 'text/html':
                data = part['body'].get('data', '')
                if data:
                    html_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    else:
        # Single part email
        data = payload['body'].get('data', '')
        if data:
            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            if payload['mimeType'] == 'text/plain':
                plain_body = decoded
            elif payload['mimeType'] == 'text/html':
                html_body = decoded

    # OPTION A — BeautifulSoup (preferred for real world HTML)
    if plain_body:
        return plain_body
    elif html_body:
        soup = BeautifulSoup(html_body, 'html.parser')
        return soup.get_text(separator=' ', strip=True)

    # OPTION B — Regex (weaker, breaks on messy HTML)
    # elif html_body:
    #     clean = re.sub(r'<[^>]+>', ' ', html_body)
    #     clean = re.sub(r'\s+', ' ', clean).strip()
    #     return clean

    return "[No readable body found]"


def main():
    print("Starting Email Fetcher...........")
    service = authenticate_gmail()
    emails = fetch_emails(service, max_results=5)

    classified_emails = classify_all_email(emails)

    display_classified_emails(classified_emails)

    print(f"\n{'='*60}")
    for i, email in enumerate(emails, 1):
        print(f"\nEmail {i}:")
        print(f"  From   : {email['sender']}")
        print(f"  Subject: {email['subject']}")
        print(f"  Date   : {email['date']}")
        print(f"  Body   : {email['body'][:200]}...")
        print(f"{'='*60}")


if __name__ == '__main__':
    main()
