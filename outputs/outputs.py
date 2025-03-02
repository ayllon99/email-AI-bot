"""
THIS IS ONLY FOR TESTING PURPOSES

"""

import os
from dotenv import load_dotenv
import sqlite3
import pandas as pd

load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH')

def extracted_emails():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT *
        FROM extracted_emails_table
        """)
    df = pd.DataFrame(cursor.fetchall())
    df.columns = ['email_id', 'thread_id', 'labels', 'sent_datetime', 'subject', 'sender', 'email_from', 'body', 'processed', 'extraction_timestamp']
    conn.commit()
    conn.close()
    return df


def responses():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT *
        FROM agent_responses
        """)
    df = pd.DataFrame(cursor.fetchall())
    df.columns = ['email_id', 'summary', 'affirmative_reply', 'negative_reply', 'processing_timestamp']
    
    summary = responses_df['summary'].loc[0]
    affirmative = responses_df['affirmative_reply'].loc[0]
    negative = responses_df['negative_reply'].loc[0]

    with open('outputs/summary_response.txt','w') as file:
        file.write(summary)

    with open('outputs/affirmative_response.txt','w') as file:
        file.write(affirmative)

    with open('outputs/negative_response.txt','w') as file:
        file.write(negative)

    conn.commit()
    conn.close()
    return df

extracted_df = extracted_emails()

responses_df = responses()

