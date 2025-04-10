import getpass
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()


if __name__ == '__main__':
    if not os.environ.get("MISTRAL_API_KEY"):
        os.environ["MISTRAL_API_KEY"] = getpass.getpass("Enter your MISTRAL_API_KEY: ")

    model = init_chat_model("mistral-large-latest",model_provider = "mistralai")


    messages = [
            SystemMessage("Translate the following text from English to Hindi:"),
            HumanMessage("hi!"),
        ]

    response = model.invoke(messages)
    print(response.content)
