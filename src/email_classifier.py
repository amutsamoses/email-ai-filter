import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


def classify_email(email):
	"""
	sends email  data to claude and get priority classsification
	in: emil dict; sender, subject, date, body
	out: dict; priority, reason action
	err: invalid response
	"""

	email_context = f"""
	From: {email['sender']}
	Subject: {email['subject']}
	Bodt snippet: {email['body'][:300]}
	"""

	prompt = f"""
	You are an intelligent email prioritization assistant.

	Classify the following email inot exactly  one of these priority levels:
	- URGENT: Requestimeediate attention and instant reply
	- IMPORTANT: Should be added to today's task list
	- NORMAL: can be read during standard review hours
	- NOISE: Should be auto-archived and hidden from primary review

	Email details:
	{email_context}

	Respond ONLY with a JSON object in this exact format, no extra text:
	{{
		"priority": "URGENT|IMPORTANT|NORMAL|NOISE",
		"reason": "one sentence explain why",
		"action": "specific action to take"
	}}
	"""

	message = client.messages.create(
	model="claude-sonnet-4-6",
	max_tokens=1024,
	messages=[
		{"role": "user", "content": prompt}
	]
	)


	# extract the text response
	reponse_text = message.content[0].text


	# parse JSON response - claude should return clean json
	try:
		classification = json.loads(response_text)
	except json.JSONDecodeError:
		# return safe default if claude return invalid
		print(f"Warning: Could not parse claude response: {response_text}")

		classification = {
		"priority": "NORMAL",
		"reason": "Could not classify automatically",
		"action": "Review manually"
		}
	
	return classification


def classify_all_email(emails):
	"""
	classiy list of all emails
	in: list of all email dict
	out: list of all emails with classification added
	"""

	print("\nClassifying emails with claude AI..............")

	classified = []

	for i, email in enumerate(emails, 1):
		print(f" Classifying email {i}/{len(emails)}: {email['subject'][:50]}...")

		classification = classify_email(email)

		# add classificatio to email dict
		email['classification'] = classification
		classified.append(email)

def display_classified_emails(emails):
	"""
	priitns classified emails in a readable format
	in: list of classified email dict
	"""

	priority_icons = {
		'URGENT': '****',
		'IMPORTANT': '$$$$',
		'NORMAL': '####',
		'NOISE': '&&&&'
	}

	print(f"\n{'='*60}")
	print("EMAIL CLASSIFICATION RESULTS")
	print(f"\n{'='*60}")

	for i , email in enumerate(emails, 1):
		c = email['classification']
		icon = priority_icons.get(c['priority'], '🔘')


		print(f"\nEmail {i}: {icon} {c['priority']}")
		print(f"  FROM  : {email['sender']}")
		print(f"  Subject: {email['subject']}")
		print(f"  Reason : {c['reason']}")
		print(f"  Action : {c['action']}")
		print(f"{'-'*60}")
