import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH')


def create_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create extracted_emails_table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_emails (
            email_id VARCHAR PRIMARY KEY,
            thread_id VARCHAR,
            labels TEXT,  -- Store list as JSON string
            sent_datetime TIMESTAMP,
            subject TEXT,
            sender VARCHAR,
            email_from VARCHAR,
            body TEXT,
            processed BOOLEAN,
            extraction_timestamp TIMESTAMP
        )
    ''')
    
    # Create summaries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS summaries (
            summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id VARCHAR,
            model VARCHAR,
            temperature NUMERIC,
            system_prompt TEXT,
            user_prompt TEXT,
            summary TEXT,
            llm_think TEXT,
            processing_timestamp TIMESTAMP,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            reported BOOLEAN,
            FOREIGN KEY (email_id) REFERENCES extracted_emails(email_id)
        )
    ''')

    # Create reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_from TIMESTAMP,
            date_to TIMESTAMP,
            emails_reported TEXT, -- Store list as JSON string
            model VARCHAR,
            temperature NUMERIC,
            system_prompt TEXT,
            user_prompt TEXT,
            report TEXT,
            llm_think TEXT,
            report_timestamp TIMESTAMP,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER
        )
    ''')

    conn.commit()
    conn.close()


def delete_duplicates(df):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    ids = cursor.execute("SELECT email_id FROM extracted_emails").fetchall()
    existing_ids = [t[0] for t in ids]
    new_emails = df[~df['email_id'].isin(existing_ids)]

    cursor.close()
    conn.close()
    return new_emails


def insert_data(df, table_name):
    conn = sqlite3.connect(DATABASE_PATH)

    df.to_sql(
    name=table_name,
    con=conn,
    if_exists='append',
    index=False
    )

    conn.commit()
    conn.close()
    print(f'Inserted into {table_name} {len(df)} rows')


def emails_unprocessed():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    query = """SELECT 
                    email_id,
                    thread_id,
                    subject,
                    sender,
                    body,
                    sent_datetime,
                    processed
                FROM (
                    SELECT 
                        email_id,
                        thread_id,
                        subject,
                        sender,
                        body,
                        sent_datetime,
                        processed,
                        ROW_NUMBER() OVER (
                            PARTITION BY thread_id
                            ORDER BY sent_datetime DESC
                        ) AS row_num
                    FROM extracted_emails_table
                ) AS subquery
                WHERE row_num = 1 AND processed = 0
                """
    df_unprocessed = pd.DataFrame(cursor.execute(query).fetchall())
    df_unprocessed.columns = ['email_id', 'thread_id', 'subject', 'sender',
                              'body', 'sent_datetime', 'processed']
    df_unprocessed.set_index('email_id', inplace=True)
    dict_unprocessed = df_unprocessed.to_dict('index')

    cursor.close()
    conn.close()
    return dict_unprocessed


def set_true(email_ids, table_name, column_name):

    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        placeholders = ",".join("?" for _ in email_ids)
        cursor.execute(f"""
            UPDATE {table_name}
            SET {column_name} = 1
            WHERE email_id IN ({placeholders})""", email_ids)

        conn.commit()
        print(f"Updated {cursor.rowcount} rows successfully")
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Email ids to set true : ", email_ids)
    finally:
        if conn:
            conn.close()


def summaries_unreported():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    query = """SELECT 
                    s.summary_id,
                    s.email_id,
                    s.summary,
                    s.reported,
                    ee.sent_datetime
                FROM summaries as s
                LEFT JOIN extracted_emails as ee
                ON s.email_id = ee.email_id
                WHERE reported = 0
                """
    df_unreported = pd.DataFrame(cursor.execute(query).fetchall())
    df_unreported.columns = ['summary_id', 'email_id', 'summary', 'reported', 'sent_datetime']
    df_unreported.sort_values('sent_datetime', inplace=True)
    df_unreported.set_index('email_id', inplace=True)
    
    dt_from = df_unreported['sent_datetime'].min()
    dt_to = df_unreported['sent_datetime'].max()
    summaries_unreported_dict = df_unreported.to_dict('index')

    cursor.close()
    conn.close()
    return summaries_unreported_dict, dt_from, dt_to


if __name__ == '__main__':
    try:
        create_database()
        print("Database and tables created successfully!")
    except Exception as e:
        print(e)