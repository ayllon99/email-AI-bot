from database import database
from extracting_emails import extract_emails
from AI_model import AI_model_server as AI


# Extract and load new emails
service = extract_emails.authenticate_gmail()
data = extract_emails.get_emails(service=service, max_results=1)
new_emails = database.delete_duplicates(data)
if len(new_emails) > 0:
    database.insert_data(new_emails, table_name='extracted_emails')

# Check if new emails to process
#returns a dict
emails_to_process = database.emails_unprocessed()

if len(emails_to_process.keys()) > 0:
    # Send to AI model and load response
    for email_id in emails_to_process.keys():
        model = AI.ModelClient()
        summary_table = model.summarize_model(email_id, emails_to_process[email_id])
        try:
            database.insert_data(summary_table, table_name='summaries')
            database.set_true([email_id], 'extracted_emails', 'processed')
            
        except Exception as e:
            print('Error inserting data into summaries table')
            print('Summary_table: ', summary_table)
        
        """ INACTIVE FOR TESTING 
        affirmative_table = model.affirmative_model(email_id, emails_to_process[email_id])
        try:
            database.insert_data(affirmative_table, table_name='affirmative_drafts')
        except Exception as e:
            print('Error inserting data into affirmative_drafts table')
            print('Affirmative_table: ', affirmative_table)
        
        negative_table = model.negative_model(email_id, emails_to_process[email_id])
        try:
            database.insert_data(negative_table, table_name='negative_drafts')
        except Exception as e:
            print('Error inserting data into negative_drafts table')
            print('Negative_table: ', negative_table)
        """
##########################################################



