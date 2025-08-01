import base64
import re
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os.path

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailPromoFilter:
    def __init__(self):
        self.service = self.authenticate_gmail()
        self.promo_label_id = None
        
        # Promotional keywords
        self.promo_keywords = [
            'unsubscribe', 'sale', 'discount', 'offer', 'deal', 'promo',
            'marketing', 'newsletter', 'limited time', 'act now', 'buy now',
            'free shipping', 'exclusive', 'special offer', 'save money',
            'click here', 'shop now', 'don\'t miss out'
        ]
        
        # Sender patterns that indicate promotional emails
        self.promo_senders = [
            r'noreply.*@', r'marketing.*@', r'promo.*@', r'deals.*@',
            r'newsletter.*@', r'notifications.*@', r'donotreply.*@'
        ]
    
        # Whitelist important senders
        self.important_senders = [
            'bank', 'paypal', 'amazon', 'receipt', 'invoice',
            'confirmation', 'security', 'alert', 'billing'
        ]
        
        # Initialize or create the promotional label
        self.setup_promotional_label()
    
    def setup_promotional_label(self):
        """Create or find the 'Promotional-Review' label"""
        label_name = 'Promotional-Review'
        
        try:
            # Get all labels
            labels = self.service.users().labels().list(userId='me').execute()
            existing_labels = labels.get('labels', [])
            
            # Check if label already exists
            for label in existing_labels:
                if label['name'] == label_name:
                    self.promo_label_id = label['id']
                    print(f"Found existing label: {label_name}")
                    return
            
            # Create new label if it doesn't exist
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show',
                'color': {
                    'backgroundColor': '#ff6d01',  # Orange background
                    'textColor': '#ffffff'        # White text
                }
            }
            
            created_label = self.service.users().labels().create(
                userId='me', body=label_object
            ).execute()
            
            self.promo_label_id = created_label['id']
            print(f"Created new label: {label_name}")
            
        except Exception as e:
            print(f"Error setting up label: {e}")
            self.promo_label_id = None
    
    def authenticate_gmail(self):
        """Authenticate and return Gmail API service"""
        creds = None
        
        # Load existing credentials
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def is_promotional(self, message_data):
        """Determine if an email is promotional"""
        subject = message_data.get('subject', '').lower()
        sender = message_data.get('sender', '').lower()
        snippet = message_data.get('snippet', '').lower()
        
        # Check for important senders first (whitelist)
        for important in self.important_senders:
            if important in sender or important in subject:
                return False
        
        # Check promotional keywords in subject
        promo_score = 0
        for keyword in self.promo_keywords:
            if keyword in subject:
                promo_score += 2
            if keyword in snippet:
                promo_score += 1
        
        # Check sender patterns
        for pattern in self.promo_senders:
            if re.search(pattern, sender):
                promo_score += 3
        
        # Check for unsubscribe links
        if 'unsubscribe' in snippet and 'http' in snippet:
            promo_score += 3
        
        # Return True if promotional score is high enough
        return promo_score >= 3
    
    def get_message_data(self, message_id):
        """Extract relevant data from a message"""
        message = self.service.users().messages().get(
            userId='me', id=message_id, format='metadata'
        ).execute()
        
        headers = message['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        
        return {
            'subject': subject,
            'sender': sender,
            'snippet': message.get('snippet', '')
        }
    
    def filter_and_label_promotional(self, max_results=100, days_back=7):
        """Find and label promotional emails for manual review"""
        if not self.promo_label_id:
            print("Error: Could not set up promotional label")
            return 0
        
        # Search for recent emails that don't already have the promotional label
        query = f'newer_than:{days_back}d -label:promotional-review'
        results = self.service.users().messages().list(
            userId='me', 
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        labeled_count = 0
        
        print(f"Checking {len(messages)} messages from the last {days_back} days...")
        
        for msg in messages:
            try:
                message_data = self.get_message_data(msg['id'])
                
                if self.is_promotional(message_data):
                    # Add promotional label
                    self.service.users().messages().modify(
                        userId='me', 
                        id=msg['id'],
                        body={'addLabelIds': [self.promo_label_id]}
                    ).execute()
                    
                    labeled_count += 1
                    print(f"Labeled: {message_data['subject'][:50]}...")
                    print(f"  From: {message_data['sender'][:30]}...")
                    
            except Exception as e:
                print(f"Error processing message: {e}")
        
        print(f"\nTotal promotional emails labeled: {labeled_count}")
        print(f"Review them in Gmail under the 'Promotional-Review' label")
        return labeled_count
    
    def bulk_delete_labeled_emails(self, confirm=True):
        """Delete all emails with the promotional label after confirmation"""
        if not self.promo_label_id:
            print("Error: Promotional label not found")
            return 0
        
        # Get all messages with the promotional label
        results = self.service.users().messages().list(
            userId='me',
            labelIds=[self.promo_label_id]
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("No promotional emails found to delete")
            return 0
        
        print(f"Found {len(messages)} emails labeled as promotional")
        
        if confirm:
            response = input(f"Are you sure you want to delete {len(messages)} emails? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Deletion cancelled")
                return 0
        
        deleted_count = 0
        for msg in messages:
            try:
                self.service.users().messages().trash(
                    userId='me', id=msg['id']
                ).execute()
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting message: {e}")
        
        print(f"Successfully deleted {deleted_count} promotional emails")
        return deleted_count
    
    def remove_promotional_labels(self, confirm=True):
        """Remove promotional labels from emails (if you want to keep them)"""
        if not self.promo_label_id:
            print("Error: Promotional label not found")
            return 0
        
        results = self.service.users().messages().list(
            userId='me',
            labelIds=[self.promo_label_id]
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("No promotional emails found to unlabel")
            return 0
        
        print(f"Found {len(messages)} emails labeled as promotional")
        
        if confirm:
            response = input(f"Remove promotional label from {len(messages)} emails? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Operation cancelled")
                return 0
        
        unlabeled_count = 0
        for msg in messages:
            try:
                self.service.users().messages().modify(
                    userId='me', 
                    id=msg['id'],
                    body={'removeLabelIds': [self.promo_label_id]}
                ).execute()
                unlabeled_count += 1
            except Exception as e:
                print(f"Error removing label: {e}")
        
        print(f"Removed promotional label from {unlabeled_count} emails")
        return unlabeled_count
    
    def show_labeled_summary(self):
        """Show summary of emails labeled as promotional"""
        if not self.promo_label_id:
            print("Error: Promotional label not found")
            return
        
        results = self.service.users().messages().list(
            userId='me',
            labelIds=[self.promo_label_id],
            maxResults=10
        ).execute()
        
        messages = results.get('messages', [])
        total_count = results.get('resultSizeEstimate', 0)
        
        print(f"\n=== Promotional Email Summary ===")
        print(f"Total labeled emails: {total_count}")
        print(f"Showing first {min(len(messages), 10)} emails:\n")
        
        for i, msg in enumerate(messages[:10], 1):
            try:
                message_data = self.get_message_data(msg['id'])
                print(f"{i}. Subject: {message_data['subject'][:60]}...")
                print(f"   From: {message_data['sender'][:50]}...")
                print()
            except Exception as e:
                print(f"{i}. Error retrieving message: {e}")
                print()

# Usage example
if __name__ == "__main__":
    filter_tool = GmailPromoFilter()
    
    print("Gmail Promotional Email Filter - Label Mode")
    print("=" * 45)
    
    while True:
        print("\nChoose an option:")
        print("1. Scan and label promotional emails")
        print("2. Show summary of labeled emails")
        print("3. Bulk delete all labeled emails")
        print("4. Remove promotional labels (keep emails)")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            days = input("Scan emails from how many days back? (default 7): ").strip()
            days = int(days) if days.isdigit() else 7
            
            max_emails = input("Maximum emails to scan? (default 100): ").strip()
            max_emails = int(max_emails) if max_emails.isdigit() else 100
            
            filter_tool.filter_and_label_promotional(max_emails, days)
            
        elif choice == '2':
            filter_tool.show_labeled_summary()
            
        elif choice == '3':
            filter_tool.bulk_delete_labeled_emails()
            
        elif choice == '4':
            filter_tool.remove_promotional_labels()
            
        elif choice == '5':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")
