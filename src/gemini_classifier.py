from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini with your API key
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))



def classify_email_ai(email):
    """
    Classifies email using Gemini AI
    IN: email dictionary with sender, subject, body
    returns: dictionary with priority, reason, action
    invalid if: API key missing, quota exceeded, invalid JSON response
    """

    # Only send what matters — cost and privacy control
    email_context = f"""
    From: {email['sender']}
    Subject: {email['subject']}
    Body snippet: {email['body'][:300]}
    """

    prompt = f"""
    You are an intelligent email prioritization assistant.

    Classify the following email into exactly one priority level:
    - URGENT: Requires immediate attention and instant reply
    - IMPORTANT: Should be added to today's task list
    - NORMAL: Can be read during standard review hours
    - NOISE: Should be auto-archived and hidden from primary view

    Email details:
    {email_context}

    Respond ONLY with a JSON object in this exact format, no extra text,
    no markdown, no backticks:
    {{
        "priority": "URGENT or IMPORTANT or NORMAL or NOISE",
        "reason": "one sentence explaining why",
        "action": "specific action to take"
    }}
    """

    try:
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        response_text = response.text.strip()

        # Strip markdown backticks if Gemini adds them
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        classification = json.loads(response_text)

        # Validate priority value is one of our four levels
        valid_priorities = ['URGENT', 'IMPORTANT', 'NORMAL', 'NOISE']
        if classification.get('priority') not in valid_priorities:
            classification['priority'] = 'NORMAL'

        return classification

    except json.JSONDecodeError as e:
        print(f"  Warning: Could not parse Gemini response: {e}")
        return {
            'priority': 'NORMAL',
            'reason': 'Could not classify automatically',
            'action': 'Review manually'
        }
    except Exception as e:
        print(f"  Error calling Gemini API: {e}")
        return {
            'priority': 'NORMAL',
            'reason': 'API error during classification',
            'action': 'Review manually'
        }


def classify_all_emails_ai(emails):
    """
    Classifies a list of emails using Gemini AI
    IN:list of email dictionaries
    returns: list of emails with classification added
    """
    print("\nClassifying emails with Gemini AI...........")

    for i, email in enumerate(emails, 1):
        print(f"  Classifying {i}/{len(emails)}: {email['subject'][:50]}...")
        email['classification'] = classify_email_ai(email)

    return emails


def display_ai_results(emails):
    """
    Prints AI classified emails grouped by priority
    retuens: list of classified email dictionaries
    """
    priority_icons = {
        'URGENT': '🔴',
        'IMPORTANT': '🟡',
        'NORMAL': '🟢',
        'NOISE': '⚫'
    }

    grouped = {'URGENT': [], 'IMPORTANT': [], 'NORMAL': [], 'NOISE': []}
    for email in emails:
        p = email['classification']['priority']
        if p in grouped:
            grouped[p].append(email)

    print(f"\n{'='*60}")
    print("AI EMAIL CLASSIFICATION RESULTS (Gemini)")
    print(f"{'='*60}")

    for priority in ['URGENT', 'IMPORTANT', 'NORMAL', 'NOISE']:
        group = grouped[priority]
        icon = priority_icons[priority]
        print(f"\n{icon} {priority} ({len(group)} emails)")
        print(f"{'-'*40}")

        if not group:
            print("  None")
            continue

        for email in group:
            c = email['classification']
            print(f"  From   : {email['sender']}")
            print(f"  Subject: {email['subject']}")
            print(f"  Reason : {c['reason']}")
            print(f"  Action : {c['action']}")
            print()
