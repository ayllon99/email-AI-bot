import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_PATH = os.getenv('DATABASE_PATH')

def create_database():
    # Connect to SQLite database (creates if not exists)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Create extracted_emails_table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_emails_table (
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
    
    # Create agent_responses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_responses (
            email_id VARCHAR,
            summary TEXT,
            affirmative_reply TEXT,
            negative_reply TEXT,
            processing_timestamp TIMESTAMP,
            FOREIGN KEY (email_id) REFERENCES extracted_emails_table(email_id)
        )
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()


def delete_duplicates(df):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    ids = cursor.execute("SELECT email_id FROM extracted_emails_table").fetchall()
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
    df_unprocessed.columns = ['email_id', 'thread_id', 'subject', 'sender', 'body', 'sent_datetime', 'processed']
    df_unprocessed.set_index('email_id', inplace=True)
    dict_df_unprocessed = df_unprocessed.to_dict('index')

    cursor.close()
    conn.close()
    return dict_df_unprocessed


def set_processed_true(email_ids):
    email_ids = tuple(email_ids)
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        placeholders = ",".join("?" for _ in email_ids)
        cursor.execute(f"""
            UPDATE extracted_emails_table
            SET processed = 1
            WHERE email_id IN ({placeholders})""", email_ids)
        
        # Commit the transaction
        conn.commit()
        
        print(f"Updated {cursor.rowcount} rows successfully")

    except Exception as e:
        print(f"Error occurred: {e}")
        print("Email ids to set true : ",email_ids)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    try:
        create_database()
        print("Database and tables created successfully!")
    except Exception as e:
        print(e)