import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# read only access from gmail
SCOPE = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIAL_FILE = "credentials.json"
TOKEN_FILE = "token.json"

def authenticate_gmail():
	""" connects to gmail and returns a service object"""
	creds = None

	# check if we have already  saved the token from previous login
	if os.path.exists("token.json"):
		creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPE)

	# if invalid credentials as user to login
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token():
			# if token expired lets refresh it silently
			print("Token expired: Silently refreshing access token.....")
			
			try:
				creds.refresh(Request())
			except:
				print(f"failed to refresh the token: {e}, re-login")
				creds = None
		if not creds:
			print("No valid token found, Initializing browser authentication flow...")
			# if for the first time , open brownser for authentication
			flow = InstalledAppFlow.from_client_secrets_file(CREDENTIAL_FILE, SCOPE)
			os.environ['BROWSER'] = '/mnt/c/Program Files/Google/Chrome/Application/chrome.exe'
			creds = flow.run_local_server(port=0, open_browser=False)
		# save token for next time login
		with open(TOKEN_FILE, "w") as token:
			token.write(creds.to_json())
			print(f"Access token securely cached to '{TOKEN_FILE}'")
	# lets build gmail service
	service = build("gmail", "v1", credentials=creds)
	return service

def main():
	print("Connecting to the gmail...........")

	try:
		service = authenticate_gmail()
		print("Connection Successfull============")
	
		# lets check it out from our profile to confirm we are connected
		profile = service.users().getProfile(userId="me").execute()

		print("==============USER PROFILE DATA===========")
		print(f"connected as: {profile['emailAddress']}")
		print(f"Total Messages: {profile['messagesTotal']}")
		print("=============================================")

	except HttpError as error:
		print(f"\n[API ERROR] Google server rejected request: {error}")
	except FileNotFoundError:
		print(f"\n[System Error] Critical file missing: make sure '{CREDENTIAL_FILE}")
	except Exception as e:
		print(f"\n[Unexpected error] something wnet wrong: {e}")

if __name__ == "__main__":
	main()
