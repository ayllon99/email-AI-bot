from openai import OpenAI
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()

BASE_URL=os.getenv('BASE_URL')
API_KEY=os.getenv('API_KEY')
SUMMARIZE_PROMPT_PATH = os.getenv('SUMMARIZE_PROMPT_PATH')
AFFIRMATIVE_PROMPT_PATH = os.getenv('AFFIRMATIVE_PROMPT_PATH')
NEGATIVE_PROMPT_PATH = os.getenv('NEGATIVE_PROMPT_PATH')


class ModelClient:
    def __init__(self):
        self.client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

    def _get_summarize_prompt(self):
        # System prompt to give context to the AI agent
        try:
            with open(SUMMARIZE_PROMPT_PATH, "r") as file:
                return file.read()
        except Exception as e:
            print(e)

    def _get_affirmative_prompt(self):
        # System prompt to give context to the AI agent
        try:
            with open(AFFIRMATIVE_PROMPT_PATH, "r") as file:
                return file.read()
        except Exception as e:
            print(e)

    def _get_negative_prompt(self):
        # System prompt to give context to the AI agent
        try:
            with open(NEGATIVE_PROMPT_PATH, "r") as file:
                return file.read()
        except Exception as e:
            print(e)

    def _process_email(self, email, target):
        sender = email['sender']
        subject = email['subject']
        body = email['body']

        if target == 'summarize':
            system_prompt = self._get_summarize_prompt()
        elif target == 'reply_affirmative':
            system_prompt = self._get_affirmative_prompt()
            target = 'reply affirmative to'
        elif target == 'reply_negative':
            system_prompt = self._get_negative_prompt()
            target = 'reply negative to'

        completion = self.client.chat.completions.create(
          model="Qwen/CodeQwen1.5-7B-Chat-GGUF",
          messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""{target} this email: 
                                            Sender: {sender}
                                            Subject: {subject}
                                            Body: {body}"""}
          ],
          temperature=0.8,
        )

        llm_response = completion.choices[0].message.content
        return llm_response
    
    def to_AI_model(self, emails_to_process):
        to_db = pd.DataFrame()
        for a in emails_to_process.keys():
            email_id = a
            summary = self._process_email(email=emails_to_process[a],
                                          target='summarize')
            affirmative_reply = self._process_email(email=emails_to_process[a],
                                                 target='reply_affirmative')
            negative_reply = self._process_email(email=emails_to_process[a],
                                                 target='reply_negative')
            processing_timestamp = datetime.now().isoformat()
            df_email = pd.DataFrame({'email_id':[email_id],
                                     'summary':[summary],
                                     'affirmative_reply':[affirmative_reply],
                                     'negative_reply':[negative_reply],
                                     'processing_timestamp':[processing_timestamp]})

            to_db = pd.concat([to_db, df_email])
        return to_db
