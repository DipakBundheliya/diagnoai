import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
# from backend.app.models.mongodb import get_chat_history , save_chat_history # Run this command for get root directory at parent folder : export PYTHONPATH=$(pwd)
# Load environment variables from .env file
load_dotenv()

# Access variable 
groq_key = os.getenv("GROQ_API_KEY") 

# Initialize llm
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=1024,
    timeout=10,
    max_retries=2,
)

def load_system_prompt():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "system_prompt.txt")  # Construct full path

    with open(file_path , "r") as file:
        return file.read()

# create langchain chatprompttemplate
system_prompt = load_system_prompt() 
chat_prompt = ChatPromptTemplate.from_template(system_prompt)

def get_history(user_id):
    # Fetch history from MongoDB
    from backend.app.models.mongodb import get_chat_history 
    history = get_chat_history(user_id)
    if not history:
        return ""
    return history

def get_ai_response(query , user_id):
    history = get_history(user_id) 
    formatted_prompt = chat_prompt.format(history=history , query=query)
    llm_response = llm.invoke(formatted_prompt).content

    from backend.app.models.mongodb import save_chat_history
    save_chat_history(user_id , query , llm_response) 
    
    return json.loads(llm_response)

def get_summary(text):
    # Fetch summary from MongoDB
    llm_inp = "Summarize below content upto max 2 lines ,do not unnecessary words or sentences \n" + text
    summary = llm.invoke(llm_inp).content
    summary = "Summary of previous conversation : " + summary
    return summary

# response_json = get_ai_response(query="I feel unwell" , user_id="11221122") 
while True:
    query = input("ask questions , type end to exit")
    if query == "end":
        break
    response_json = get_ai_response(query=query , user_id="11221122")
    print(response_json) 