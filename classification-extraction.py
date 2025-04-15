import os
from enum import Enum
from typing import Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

class Mood(str, Enum):
    happy = "happy"
    sad = "sad"
    neutral = "neutral"

class Insight(BaseModel):
    sentiment: Mood = Field(description="Mood of the text")
    aggressiveness: int = Field(description="Aggressiveness level (1–10)")
    language: str
    person: str
    date: str
    location: str
    organization: str

class Analyzer:
    def __init__(self):
        model = init_chat_model("mistral-large-latest", model_provider="mistralai")
        self.chain = model.with_structured_output(Insight)
        self.prompt = ChatPromptTemplate.from_template("""
Extract the following from the input:
- sentiment (happy/sad/neutral)
- aggressiveness (1–10)
- language, person, date, location, organization
Respond using the fields in 'Insight'.

Input:
{input}
""")

    def run(self, text: str) -> Dict[str, Any]:
        prompt = self.prompt.invoke({"input": text})
        return self.chain.invoke(prompt).model_dump()

def main():
    if not os.getenv("MISTRAL_API_KEY"):
        print("MISTRAL_API_KEY missing.")
        return

    text = input("🔍 Enter text to analyze:\n> ")
    result = Analyzer().run(text)

    print("\n📊 Results:")
    for k, v in result.items():
        print(f"{k.capitalize()}: {v}")

if __name__ == "__main__":
    main()
