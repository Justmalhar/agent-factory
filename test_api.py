import logging
from utils.openai_client import create_openai_client, generate_content

logging.basicConfig(level=logging.INFO)

def test_api(api_key):
    try:
        client = create_openai_client(api_key)
        response = generate_content(
            client,
            "You are a helpful assistant.",
            "Say hello!",
            "meta-llama/llama-3.1-405b-instruct:free"
        )
        print("Response:", response)
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    api_key = input("Enter your OpenRouter API key: ")
    test_api(api_key) 