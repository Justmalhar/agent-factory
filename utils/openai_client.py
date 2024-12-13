from openai import OpenAI
import os
import logging
import time

def create_openai_client(api_key):
    try:
        return OpenAI(
            api_key=api_key,
        )
    except Exception as e:
        logging.error(f"Error creating OpenAI client: {str(e)}")
        raise Exception(f"Failed to initialize OpenAI client: {str(e)}")

def generate_content(client, system_prompt, user_prompt, model="gpt-4o-mini"):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000,
            stream=True
        )
        
        # Return a generator for streaming
        return completion
        
    except Exception as e:
        logging.error(f"Error generating content: {str(e)}")
        return None

def read_prompt(prompt_file):
    try:
        with open(f"prompts/{prompt_file}.md", "r") as f:
            content = f.read().strip()
            if not content:
                raise Exception(f"Prompt file {prompt_file}.md is empty")
            return content
    except FileNotFoundError:
        error_msg = f"Prompt file {prompt_file}.md not found"
        logging.error(error_msg)
        return error_msg
    except Exception as e:
        logging.error(f"Error reading prompt file: {str(e)}")
        return f"Error reading prompt: {str(e)}" 