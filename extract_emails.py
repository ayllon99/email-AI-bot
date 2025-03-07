from database import database
from extracting_emails import extract_emails


# Extract and drop duplicates
service = extract_emails.authenticate_gmail()
data = extract_emails.get_emails(service=service, max_results=1)
new_emails = database.delete_duplicates(data)

# Check if new emails
if len(new_emails) > 0:
    database.insert_data(new_emails, table_name='extracted_emails')
