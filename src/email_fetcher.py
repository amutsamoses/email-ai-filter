
import base64
from gmail_connect import authenticate_gmail
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup

def fetch_emails(service, max_results=10):
	"""
	fetches latest emails form inbox, number of emails fetch
	list of parsed email dicts
	
	"""
	if not service:
		print("[Error] Gmail service object is missing or invalid.")
		return []

	print(f"\n Fetching last {max_results} emails...........")

	# get liat of meassages ids from inbox
	try:
		results = service.users().messages().list(
		userId='me',
		labelIds=['INBOX'], maxResults=max_results
		).execute()


		# extract message list
		messages = results.get('messages', [])

		if not messages:
			print("No messages found, current inbox empty......")
			return []
		print(f"Found {len(messages)} messages, Parsing..........")

		# fetch full details for each messages
		emails = []
		for msg in messages:
			try:
				email_data = parse_email(service, msg['id'])
				emails.append(email_data)
			except HttpError as msg_err:
				print(f"[Warning] Skipped msg ID {msg['id']}API error: {msg_err}")
				continue

		return emails

	except HttpError as api_err:
		print(f"[API ERROR] Failed to retreive email list: {api_err}")
		return []

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
	extract readable text from the email, recursively
	"""

	# body = ""

	raw_body = ""

	if payload.get('mimeType') == 'text/plain':
		data = payload['body'].get('data', '')
		if data:
			raw_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

	# email can have direct body or multiple parts
	elif 'parts' in payload:
		for part in payload['parts']:
			body = extract_body(part)
			if body and body != "[No readable body found]":
				raw_body = body
				break
			# if part['mimeType'] == 'text/plain':
				# data =  part['body'].get('data', '')
				# if data:
					# gmail decodes with base64
					# body = base64.urlsafe_b64decode(data).decode('utf-8', 
					# errors='ignore'	
					# )
					# break	

	# check top-level body if no parts array exist
	else:
		data = payload.get('body', {}). get('data', '')
		if data:
			raw_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

	if not raw_body or raw_body == "[No readable body found]":
		return "[No readablr boby found]"

	if "<html>" in raw_body or "<doctype>" in raw_body or "<body>" in raw_body.lower():
		soup = BeautifulSoup(raw_body, "html.parser")

		cleaned_text = soup.get_text(separator="", strip=True)

		return cleaned_text

	return raw_body

	# else:
		# data = payload['body'].get('data', '')
		# if data:
			# body = base64.urlsafe_b64decode(data).decode('utf-8', errors='igonre')

	# return body if body else "[No readablr body found]"


def main():
	print("============================================")
	print("Starting Email fetcher Pipleines............")
	print("============================================")


	service = authenticate_gmail()

	emails = fetch_emails(service, max_results=7)

	print(f"\n{'='*60}")
	for i, email in enumerate(emails, 1):
		# print(f"\nEmail {i}:")
		print(f"\n[{i}]  Frome  : {email['sender']}")
		print(f"  Subject: {email['subject']}")
		print(f"  Date   : {email['date']}")
		print(f"  Body   : {email['body'][:150]}...")
		print('=' * 60)

if __name__ == '__main__':
	main()
