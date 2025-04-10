import os
from pymongo import MongoClient
from mistralai import Mistral
from dotenv import load_dotenv
load_dotenv()


class Chatbot:

    def __init__(self, _api_key, model, mongo_url, db_name, collection_name):
        self.api_key = _api_key
        self.model = model
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.collection_name = collection_name
        self.conversation_history = []
        self.mistral_client = Mistral(api_key=self.api_key)

        self.load_profile_context()

    def load_profile_context(self): 
        try:
            client = MongoClient(self.mongo_url)
            db = client[self.db_name]
            collection = db[self.collection_name]

            projection = {
                "firstName": 1,
                "lastName": 1,
                "areaOfExpertise": 1,
                "currentLocation": 1,
                "_id": 0
            }

            profiles = list(collection.find({}, projection))

            if not profiles:
                profile_context = "No profile data was found."
            else:
                profile_context = "Below are user profiles with key attributes:\n\n"
                for idx, profile in enumerate(profiles, start=1):
                    location = profile.get("currentLocation", {})
                    city = location.get("city", "Unknown")
                    state = location.get("state", "")
                    country = location.get("country", "")

                    profile_context += (
                        f"{idx}. Name: {profile.get('firstName', 'N/A')} {profile.get('lastName', 'N/A')}, "
                        f"Expertise: {profile.get('areaOfExpertise', 'N/A')}, "
                        f"Location: {city}, {state}, {country}\n"
                    )
                profile_context += "\nYou can answer questions using this profile list."

            system_message = {
                "role": "system",
                "content": profile_context.strip()
            }
            self.conversation_history.append(system_message)
            print(f"Loaded {len(profiles)} profiles into context.")
        except Exception as e:
            print("Error loading profile context:", e)
            self.conversation_history.append({
                "role": "system",
                "content": "There was an issue retrieving profile data."
            })

    def get_user_input(self):
        user_input = input("\nYou: ")
        user_message = {
            "role": "user",
            "content": user_input
        }
        self.conversation_history.append(user_message)
        return user_message

    def send_request(self):
        try:
            stream = self.mistral_client.chat.stream(
                model=self.model,
                messages=self.conversation_history
            )
            response_buffer = ""
            for chunk in stream:
                content = chunk.data.choices[0].delta.content
                print(content, end="")
                response_buffer += content

            if response_buffer.strip():
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response_buffer
                })
        except Exception as e:
            print("Error during chat requests:", e)

    def run(self):
        while True:
            self.get_user_input()
            self.send_request()


if __name__ == "__main__":
    api_key = os.getenv("Mistral_API_KEY")
    mongo_url = os.getenv("MONGO_URI")
    db_name = "app-dev"
    collection_name = "profiles"

    if not api_key:
        print("Please set MISTRAL_API_KEY in your environment.")
        exit(1)

    if not mongo_url:
        print("Please set MONGO_CONNECTION_STRING in your environment.")
        exit(1)

    chat_bot = Chatbot(api_key, "mistral-large-latest", mongo_url, db_name, collection_name)
    chat_bot.run()
