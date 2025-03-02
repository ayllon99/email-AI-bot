# Outputs

## Model

In the test, I have used a self-hosted LLM model: Qwen/CodeQwen1.5-7B-Chat-GGUF/codeqwen-1_5-7b-chat-q4_0.gguf

This model use just 4GB VRAM so it is a very lightweight model and we should get better results with something bigger like newer models of openai, or deepseek.

## Examples

In the first example I've just process an email stored in (email_to_reply.txt)

Outputs are stored in summary_response.txt, affirmative_response.txt and negative_response.txt

## Notes about outputs

As I mentioned above, this is a lightweight model so outputs are not as accurate as we could get.
Due to this (or not a good enough prompt), affirmative_response and negative_response are not responses to the email but the same email with a different focus.
