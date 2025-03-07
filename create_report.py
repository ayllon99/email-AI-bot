from database import database
from AI_model import AI_model_server as AI


#Check if new summaries to report
summaries_unreported_dict, dt_from, dt_to = database.summaries_unreported()

# Send to AI model and load response
if len(summaries_unreported_dict.keys()) > 0:
    # Send to AI model and load response
    model = AI.ModelClient()
    report_table = model.generate_report(summaries_unreported_dict,
                                         dt_from, dt_to)
    try:
        database.insert_data(report_table, table_name='reports')
        database.set_true(list(summaries_unreported_dict.keys()),
                          'summaries', 'reported')
    except Exception as e:
        print('Error inserting data into reports table', e)
        print('Report_table: ', report_table)
