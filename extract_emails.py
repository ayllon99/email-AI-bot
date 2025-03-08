from database import database
from extracting_emails import get_emails


# Extract and drop duplicates
service = get_emails.authenticate_gmail()
data = get_emails.get_emails(service=service, max_results=10)
new_emails = database.delete_duplicates(data)

# Check if new emails
if len(new_emails) > 0:
    database.insert_data(new_emails, table_name='extracted_emails')
