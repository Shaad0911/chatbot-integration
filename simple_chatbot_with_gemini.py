import os
from dotenv import load_dotenv


load_dotenv()

from google import genai

if __name__ == '__main__':
    api_key = os.getenv('Mistral_API_KEY')
    if api_key is None:
        print("")
        exit(1)

    model = "mistral-large-latest"
client = genai.Client(api_key= os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="describe the best thing about bhopal",

)



print(response.text)
