import os
import getpass
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

# Load profile context from MongoDB
def load_profile_context(mongo_url, db_name, collection_name):
    try:
        client = MongoClient(mongo_url)
        db = client[db_name]
        collection = db[collection_name]

        projection = {
            "firstName": 1,
            "lastName": 1,
            "areaOfExpertise": 1,
            "currentLocation": 1,
            "_id": 0
        }

        profiles = list(collection.find({}, projection))
        if not profiles:
            return "No profile data was found."

        context = "Below are user profiles with key attributes:\n\n"
        for idx, profile in enumerate(profiles, start=1):
            location = profile.get("currentLocation", {})
            city = location.get("city", "Unknown")
            state = location.get("state", "")
            country = location.get("country", "")
            context += (
                f"{idx}. Name: {profile.get('firstName', 'N/A')} {profile.get('lastName', 'N/A')}, "
                f"Expertise: {profile.get('areaOfExpertise', 'N/A')}, "
                f"Location: {city}, {state}, {country}\n"
            )
        return context.strip()
    except Exception as e:
        print("Error loading profile context:", e)
        return "There was an issue retrieving profile data."


if __name__ == '__main__':
    if not os.environ.get("MISTRAL_API_KEY"):
        os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter your MISTRAL_API_KEY: ")

    mongo_url = os.getenv("MONGO_URI")
    db_name = os.getenv("DATABASE")
    collection_name = os.getenv("COLLECTION")

    profile_context = load_profile_context(mongo_url, db_name, collection_name)

    # Initialize Langchain chat model
    model = init_chat_model("mistral-large-latest", model_provider="mistralai")

    # Use Langchain PromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Below are user profiles:\n{profile_context}\n\nYou can now answer user queries based on this data."),
        ("human", "{question}")
    ])

    print("\nHey Shadab! Ask me anything buddy\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        # Format the prompt with dynamic values
        messages = prompt.format_messages(
            profile_context=profile_context,
            question=user_input
        )

        try:
            response = model.invoke(messages)
            print(f"buddy: {response.content}\n")
        except Exception as e:
            print("Error during chat:", e)
