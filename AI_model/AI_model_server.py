from openai import OpenAI
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()

BASE_URL = os.getenv('BASE_URL')
API_KEY = os.getenv('API_KEY')
SUMMARIZE_PROMPT_PATH = os.getenv('SUMMARIZE_PROMPT_PATH')
AFFIRMATIVE_PROMPT_PATH = os.getenv('AFFIRMATIVE_PROMPT_PATH')
NEGATIVE_PROMPT_PATH = os.getenv('NEGATIVE_PROMPT_PATH')
REPORT_PROMPT_PATH = os.getenv("REPORT_PROMPT_PATH")
MODEL = os.getenv("MODEL")
TEMPERATURE = round(float(os.getenv("TEMPERATURE")),1)


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

    def _get_report_prompt(self):
        # System prompt to give context to the AI agent
        try:
            with open(REPORT_PROMPT_PATH, "r") as file:
                return file.read()
        except Exception as e:
            print(e)

    def _process_email(self, email, mode):
        sender = email['sender']
        subject = email['subject']
        body = email['body']

        if mode == 'summary':
            system_prompt = self._get_summarize_prompt()
            target = 'summarize'
        elif mode == 'affirmative_draft':
            system_prompt = self._get_affirmative_prompt()
            target = 'reply affirmative to'
        elif mode == 'negative_draft':
            system_prompt = self._get_negative_prompt()
            target = 'reply negative to'

        user_prompt = f"""{target} this email: 
                        Sender: {sender}
                        Subject: {subject}
                        Body: {body}"""
        
        completion = self.client.chat.completions.create(
          model=MODEL,
          messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
          ],
          temperature=TEMPERATURE,
        )
        model = completion.model
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        total_tokens = completion.usage.total_tokens
        llm_response = completion.choices[0].message.content
        return {'model': model, 'temperature': TEMPERATURE,
                'system_prompt': system_prompt, 'user_prompt': user_prompt,
                mode: llm_response, 'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens, 'total_tokens': total_tokens}

    def summarize_model(self, email_id, email_to_process):

        results = self._process_email(email=email_to_process,
                                        mode='summary')
        processing_timestamp = datetime.now().isoformat()
        results['email_id'] = email_id
        results['processing_timestamp'] = processing_timestamp
        results['reported'] = False
        summary_table = pd.DataFrame([results])

        return summary_table

    def affirmative_model(self, email_id, email_to_process):

        results = self._process_email(email=email_to_process,
                                        mode='affirmative_draft')
        processing_timestamp = datetime.now().isoformat()
        results['email_id'] = email_id
        results['processing_timestamp'] = processing_timestamp
        affirmative_table = pd.DataFrame([results])

        return affirmative_table

    def negative_model(self, email_id, email_to_process):

        results = self._process_email(email=email_to_process,
                                        mode='negative_draft')
        processing_timestamp = datetime.now().isoformat()
        results['email_id'] = email_id
        results['processing_timestamp'] = processing_timestamp
        negative_table = pd.DataFrame([results])

        return negative_table
    
    def _process_summaries(self, summaries_to_report):
        for a in summaries_to_report.keys():
            summary = summaries_to_report[a]['summary']
            # Useful in case we use deep think option
            if summary[:7] == '<think>':
                summary = summary.split('</think>')[1]

            summaries_to_report[a]['summary'] = summary

        summaries_processed = {email_id: {'summary': details['summary'],
                                          'sent_datetime': details['sent_datetime']
                                          }
                               for email_id, details in summaries_to_report.items()}
        return summaries_processed

    def generate_report(self, summaries_to_report):
        summaries_processed = self._process_summaries(summaries_to_report)

        system_prompt = self._get_report_prompt()
        user_prompt = f"""Create a report about this emails: 
                        {summaries_processed}"""
        

        completion = self.client.chat.completions.create(
          model=MODEL,
          messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
          ],
          temperature=TEMPERATURE,
        )
        model = completion.model
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        total_tokens = completion.usage.total_tokens
        llm_response = completion.choices[0].message.content
        return {'model': model, 'temperature': TEMPERATURE,
                'system_prompt': system_prompt, 'user_prompt': user_prompt,
                'report': llm_response, 'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens, 'total_tokens': total_tokens}

