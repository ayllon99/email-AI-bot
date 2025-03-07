# EMAIL BOT

## TO DO

* Check if dt_from and dt_to are working properly

## Target of the project

This project aims to streamline email communication by providing two key functionalities:

* Email Summarization: Automatically summarize the content of incoming emails to quickly grasp the main points.

* Reply Drafting: Generate draft replies with an affirmative (positive) and negative focus based on the email content.

## Set up step by step

### 1. Set Up Google Cloud Project & Enable Gmail API

1. Go to the Google Cloud Console.

    - Create a new project or select an existing one.

    - Enable the Gmail API:

    - Navigate to APIs & Services > Library.

    - Search for "Gmail API" and enable it.

    - Create OAuth 2.0 Credentials:

    - Go to APIs & Services > Credentials.

    - Click Create Credentials > OAuth client ID.

    - Choose Desktop App as the application type.

    - Download the credentials JSON file (rename it to credentials.json).

2. Install Required Libraries

    ```bash
    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
    ```

3. Add Your Email as a Test User
     - Go to the Google Cloud Console.

     - Select your project.

     - Navigate to APIs & Services > OAuth consent screen.

     - In the Test users section, click + Add Users.

     - Add your email and click Save.

4. Notes
Quotas: The Gmail API has daily quotas (1,000,000 requests/day for most users).

### 2. Create your database

```bash
python3 database/database.py
```

### 3. Use tool

Run main.py setting max_results to a number of emails to extract.

## Notes

- In threads we only need to process last email because all the thread is included in the last email body (To change this go to database.py in emails_unprocessed function)

- We don't have in consideration if the email has been read or not so everything is going to work properly even if you open emails before the AI process them.

- Consider each email is going to be processed 3 times by AI model: summarizing, affirmative reply and negative reply
