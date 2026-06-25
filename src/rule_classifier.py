def classify_email_rules(email):
    """
    classifies email using rule-based keyword matching
    IN: email dictionary with sender, subject, body
    OUT: dictionary with priority, reason, action
    err:email dict missing expected keys
    """

    # Extract and normalize — lowercase for case-insensitive matching
    sender = email.get('sender', '').lower()
    subject = email.get('subject', '').lower()

    # URGENT RULES
    urgent_subject_keywords = [
        'deadline', 'urgent', 'asap', 'action required'
    ]
    urgent_senders = [
        'samegavi@africantechnologyforum.org'
    ]

    if any(keyword in subject for keyword in urgent_subject_keywords):
        return {
            'priority': 'URGENT',
            'reason': 'Subject contains high-priority time-sensitive keyword',
            'action': 'Notify immediately via desktop alert and flag for instant reply',
            'matched_rule': 'urgent_subject_keyword'
        }

    if any(s in sender for s in urgent_senders):
        return {
            'priority': 'URGENT',
            'reason': 'Email from a known important contact',
            'action': 'Notify immediately via desktop alert and flag for instant reply',
            'matched_rule': 'urgent_sender'
        }

    # IMPORTANT RULES
    important_subject_keywords = [
        'invoice', 'payment', 'subscription renewal'
    ]
    important_sender_domains = [
        'udacity.com', 'kaggle.com'
    ]

    if any(keyword in subject for keyword in important_subject_keywords):
        return {
            'priority': 'IMPORTANT',
            'reason': 'Subject relates to finances or subscription',
            'action': 'Add to today\'s task list and keep at top of inbox',
            'matched_rule': 'important_subject_keyword'
        }

    if any(domain in sender for domain in important_sender_domains):
        return {
            'priority': 'IMPORTANT',
            'reason': 'From a key educational platform you actively use',
            'action': 'Add to today\'s task list and keep at top of inbox',
            'matched_rule': 'important_sender_domain'
        }

    # NOISE RULES
    noise_sender_domains = [
        'facebookmail.com', 'instagram.com', 'linkedin.com'
    ]
    noise_subject_keywords = [
        'unsubscribe', 'offer', 'sale', 'win'
    ]

    if any(domain in sender for domain in noise_sender_domains):
        return {
            'priority': 'NOISE',
            'reason': 'Social media notification, not work related',
            'action': 'Auto-archive, mark as read, hide from primary view',
            'matched_rule': 'noise_sender_domain'
        }

    if any(keyword in subject for keyword in noise_subject_keywords):
        return {
            'priority': 'NOISE',
            'reason': 'Promotional or automated marketing content',
            'action': 'Auto-archive, mark as read, hide from primary view',
            'matched_rule': 'noise_subject_keyword'
        }

    # NORMAL RULES
    normal_sender_domains = [
        'stackoverflow.email', 'microsoft.com'
    ]
    normal_subject_keywords = [
        'newsletter', 'digest', 'weekly'
    ]

    if any(domain in sender for domain in normal_sender_domains):
        return {
            'priority': 'NORMAL',
            'reason': 'Developer or community update, no immediate deadline',
            'action': 'Leave in inbox for standard review hours',
            'matched_rule': 'normal_sender_domain'
        }

    if any(keyword in subject for keyword in normal_subject_keywords):
        return {
            'priority': 'NORMAL',
            'reason': 'Newsletter or digest, good to read but not urgent',
            'action': 'Leave in inbox for standard review hours',
            'matched_rule': 'normal_subject_keyword'
        }

    # DEFAULT
    # Nothing matchedtreat as NORMAL to avoid hiding potentially
    # important emails that don't fit known patterns
    return {
        'priority': 'NORMAL',
        'reason': 'Unclassified email — no rules matched',
        'action': 'Deliver to main inbox for standard review',
        'matched_rule': 'default'
    }


def classify_all_emails_rules(emails):
    """
    WHAT: Classifies a list of emails using rule-based system
    INPUT: list of email dictionaries
    OUTPUT: list of emails with classification added
    """
    print("\nClassifying emails with rule-based system...........")

    for i, email in enumerate(emails, 1):
        print(f"  Classifying {i}/{len(emails)}: {email['subject'][:50]}...")
        email['classification'] = classify_email_rules(email)

    return emails


def display_results(emails):
    """
    Prints classified emails grouped by priority
    IN: list of classified email dictionaries
    """
    priority_icons = {
        'URGENT': '🔴',
        'IMPORTANT': '🟡',
        'NORMAL': '🟢',
        'NOISE': '⚫'
    }

    # Group by priority
    grouped = {'URGENT': [], 'IMPORTANT': [], 'NORMAL': [], 'NOISE': []}
    for email in emails:
        p = email['classification']['priority']
        grouped[p].append(email)

    print(f"\n{'='*60}")
    print("EMAIL CLASSIFICATION RESULTS")
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
            print(f"  Rule   : {c['matched_rule']}")
            print(f"  Action : {c['action']}")
            print()
