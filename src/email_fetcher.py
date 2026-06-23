
import base64
from gmail_connect import authenticate_gmail

def fetch_emails(service, max_results=10):
	"""
	fetches latest emails form inbox, number of emails fetch
	list of parsed email dicts
	
	"""

	print(f"\n Fetching last {max_results} emails...........")

	# liat of meassages ids from inbox
	results = service.users().messages().list(
	userId='me',
	labelIds=['INBOX'], maxResults=max_results
	).execute()


	# extract message list
	messages = results.get('messages', [])

	if not messages:
		print("No messages found......")
		return []
	print(f"Found {len(messages)} messages, Parsing..........")

	# fetch full details for each messages
	emails = []
	for msg in messages:
		email_data = parse_email(service, msg['id'])
		emails.append(email_data)

	return emails

def parse_email(service, msg_id):
	"""
	fetches and parses single  email id
	out: dict with subject sender date and body 
	"""

	# fetches the full message
	message = service.users().messages().get(
	userId='me', id=msg_id, format='full'
	).execute()

	headers = message['payload']['headers']

	subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')
	sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
	date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

	body = extract_body(message['payload'])

	return {
	'id': msg_id, 'subject': subject, 'sender': sender, 
	'date': date, 'body': body[:500]
	}


def extract_body(payload):
	"""
	extract readable text from the email
	"""

	body = ""

	# email can have direct body or multiple parts
	if 'parts' in payload:
		for part in payload['parts']:
			if part['mimeType'] == 'text/plain':
				data =  part['body'].get('data', '')
				if data:
					# gmail decodes with base64
					body = base64.urlsafe_b64decode(data).decode('utf-8', 
					errors='ignore'	
					)
					break	


	else:
		data = payload['body'].get('data', '')
		if data:
			body = base64.urlsafe_b64decode(data).decode('utf-8', errors='igonre')

	return body if body else "[No readablr body found]"


def main():
	print("Starting Email fetcher...........")

	service = authenticate_gmail()

	emails = fetch_emails(service, max_results=5)

	print(f"\n{'='*60}")
	for i, email in enumerate(emails, 1):
		print(f"\nEmail {i}:")
		print(f"  Frome  : {email['sender']}")
		print(f"  Subject: {email['subject']}")
		print(f"  Date   : {email['date']}")
		print(f"  Body   : {email['body'][:200]}...")
		print(f"{'='*60}")

if __name__ == '__main__':
	main()
