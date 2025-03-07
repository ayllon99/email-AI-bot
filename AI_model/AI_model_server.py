from openai import OpenAI
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
from groq import Groq
import json


load_dotenv()

#BASE_URL = os.getenv('BASE_URL')
API_KEY = os.getenv('API_KEY')
SUMMARIZE_PROMPT_PATH = os.getenv('SUMMARIZE_PROMPT_PATH')
REPORT_PROMPT_PATH = os.getenv("REPORT_PROMPT_PATH")
MODEL = os.getenv("MODEL")
TEMPERATURE = round(float(os.getenv("TEMPERATURE")),1)


class ModelClient:
    def __init__(self):
        self.client = Groq(api_key=API_KEY)        

    def _get_report_prompts(self, summaries_processed):
        # System prompt to give context to the AI agent
        try:
            with open(REPORT_PROMPT_PATH, "r") as file:
                system_prompt = file.read()
        except Exception as e:
            print(e)

        user_prompt = f"{summaries_processed}"
        return system_prompt, user_prompt

    def _get_summary_prompts(self, email):
        try:
            with open(SUMMARIZE_PROMPT_PATH, "r") as file:
                system_prompt = file.read()
        except Exception as e:
            print(e)

        sender = email['sender']
        subject = email['subject']
        body = email['body']
        user_prompt = f"""Sender: {sender}
                          Subject: {subject}
                          Body: {body}"""
        
        return system_prompt,user_prompt

    def _send_to_AI(self, mode, system_prompt, user_prompt):        
        completion = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=TEMPERATURE,
            stream=False,
            reasoning_format='parsed'
            )

        model = completion.model
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens
        total_tokens = completion.usage.total_tokens
        llm_response = completion.choices[0].message.content
        llm_think = completion.choices[0].message.reasoning

        return {'model': model, 'temperature': TEMPERATURE,
                'system_prompt': system_prompt, 'user_prompt': user_prompt,
                mode: llm_response, 'llm_think': llm_think, 'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens, 'total_tokens': total_tokens}

    def generate_summary(self, email_id, email_to_process):
        system_prompt, user_prompt = self._get_summary_prompts(email_to_process)
        results = self._send_to_AI(mode='summary',
                                   system_prompt=system_prompt,
                                   user_prompt=user_prompt)
        processing_timestamp = datetime.now().isoformat()
        results['email_id'] = email_id
        results['processing_timestamp'] = processing_timestamp
        results['reported'] = False

        return pd.DataFrame([results])

    def _process_summaries(self, summaries_to_report):
        summaries_processed = {email_id: {'summary': details['summary'],
                                          'sent_datetime': details['sent_datetime']
                                          }
                               for email_id, details in summaries_to_report.items()}
        return summaries_processed

    def generate_report(self, summaries_unreported_dict, dt_from, dt_to):
        emails_reported = json.dumps(list(summaries_unreported_dict.keys()))
        summaries_processed = self._process_summaries(summaries_unreported_dict)
        system_prompt, user_prompt = self._get_report_prompts(summaries_processed)
        results = self._send_to_AI(mode='report',
                                  system_prompt=system_prompt,
                                  user_prompt=user_prompt)
        results['date_from'] = dt_from
        results['date_to'] = dt_to
        results['emails_reported'] = emails_reported
        results['report_timestamp'] = datetime.now().isoformat()
        
        return pd.DataFrame([results])

