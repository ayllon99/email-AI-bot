from database import database
from AI_model import AI_model_server as AI


# Check if new emails to process
emails_to_process = database.emails_unprocessed()

# Send to AI model and load response
for email_id in emails_to_process.keys():
    model = AI.ModelClient()
    summary_table = model.generate_summary(email_id,
                                           emails_to_process[email_id])
    try:
        database.insert_data(summary_table, table_name='summaries')
        database.set_true([email_id], 'extracted_emails', 'processed')
    except Exception as e:
        print('Error inserting data into summaries table', e)
        print('Summary_table: ', summary_table)
