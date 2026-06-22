import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# read only access from gmail
SCOPE = ["https://www.googleapis.com/auth/gmail.readonly"]


def authenticate_gmail():
	""" connects to gmail and returns a service object"""
	creds = None

	# check if we have already  saved the token from previous login
	if os.path.exists("token.json"):
		creds = Credentials.from_authorized_user_file("token.json", SCOPE)

	# if invalid credentials as user to login
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token():
			# if token expired lets refresh it silently
			creds.refresh(Request())
		else:
			# if for the first time , open brownser for authentication
			flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPE)
			os.environ['BROWSER'] = '/mnt/c/Program Files/Google/Chrome/Application/chrome.exe'
			creds = flow.run_local_server(port=0, open_browser=False)
		# save token for next time login
		with open("token.json", "w") as token:
			token.write(creds.to_json())
	# lets build gmail service
	service = build("gmail", "v1", credentials=creds)
	return service

def main():
	print("Connecting to the gmail...........")
	service = authenticate_gmail()
	print("Connection Successfull============")
	
	# lets check it out from our profile to confirm we are connected
	profile = service.users().getProfile(userId="me").execute()
	print(f"connected as: {profile['emailAddress']}")
	print(f"Total Messages: {profile['messagesTotal']}")


if __name__ == "__main__":
	main()
