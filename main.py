from database import database
from extracting_emails import extract_emails
from AI_model import AI_model_server as AI


# Extract and load new emails
service = extract_emails.authenticate_gmail()
data = extract_emails.get_emails(service=service, max_results=1)
new_emails = database.delete_duplicates(data)
if len(new_emails) > 0:
    database.insert_data(new_emails, table_name='extracted_emails_table')

# Check if new emails to process
emails_to_process = database.emails_unprocessed()

# Send to AI model and load response
model = AI.ModelClient()
results = model.to_AI_model(emails_to_process)
if len(results) > 0:
    database.insert_data(results, table_name='agent_responses')
    database.set_processed_true(results['email_id'])


