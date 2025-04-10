import os
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

if __name__ == '__main__':
    api_key = os.getenv('Mistral_API_KEY')
    if api_key is None:
        print("Error: Mistral API key not found.")
        exit(1)

    model = "mistral-large-latest"

    client = Mistral(api_key=api_key)

    chat_response = client.chat.stream(
        model=model,
        messages=[

            {
                "role": "user",
                "content": "What is the capital of Japan?",
            },
            {
                "role": "user",
                "content": "What is the capital of India?",
            },

        ]
    )

    # Iterate over the streaming response
    for chunk in chat_response:
       print(chunk.data.choices[0].delta.content, end="")
