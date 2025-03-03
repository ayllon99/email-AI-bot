from database import database
from extracting_emails import extract_emails
from AI_model import AI_model_server as AI
import json
from datetime import datetime
import pandas as pd


summaries_to_report, dt_from, dt_to = database.summaries_unreported()
emails_reported = json.dumps(list(summaries_to_report.keys()))

if len(summaries_to_report.keys()) > 0:
    # Send to AI model and load respons
    model = AI.ModelClient()
    results = model.generate_report(summaries_to_report)
    results['date_from'] = dt_from
    results['date_to'] = dt_to
    results['emails_reported'] = emails_reported
    results['report_timestamp'] = datetime.now().isoformat()
    reports_table = pd.DataFrame([results])
    try:
        database.insert_data(reports_table, table_name='summaries')
        database.set_true(list(summaries_to_report.keys()), 'summaries', 'reported')

    except Exception as e:
        print('Error inserting data into reports table')
        print('Reports_table: ', reports_table)

