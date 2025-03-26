import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from backend.app.models.mongodb import get_chat_history , save_chat_history # Run this command for get root directory at parent folder : export PYTHONPATH=$(pwd)
# Load environment variables from .env file
load_dotenv()

# Access variable 
groq_key = os.getenv("GROQ_API_KEY") 

# Initialize llm
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=1024,
    timeout=10,
    max_retries=2,
)

def load_system_prompt():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "system_prompt_2.txt")  # Construct full path

    with open(file_path , "r") as file:
        return file.read()

# create langchain chatprompttemplate
system_prompt = load_system_prompt() 
chat_prompt = ChatPromptTemplate.from_template(system_prompt)

def get_history(user_id):
    # Fetch history from MongoDB
    history = get_chat_history(user_id)
    if not history:
        return ""
    return history

def get_ai_response(query , user_id , max_retries=4): 
    history = get_history(user_id) 
    formatted_prompt = chat_prompt.format(history=history , query=query)

    try:
        llm_response = llm.invoke(formatted_prompt).content
        # breakpoint()
        json_response = json.loads(llm_response)
        save_chat_history(user_id , query , llm_response) 
        return json_response
    except json.JSONDecodeError as e:
        formatted_prompt = f"""
            convert below unstructured json structure to correct structure and strongly consider that you return only correct json structure without any extra single word or sentence
            Please correct it and respond ONLY with valid JSON in one of these formats:
                    
            Format 1: {{"Question": "your question", "Options": ["option1", "option2"]}}
            Format 2: {{"Disease": "disease name", "Advice": "medical advice"}}
            
            Your invalid response was:
            {llm_response}
            
            Error: {str(e)}
            
            Please provide the corrected JSON response:
            """
        for attempt in max_retries:
            try:
                re_llm_response = llm.invoke(formatted_prompt)
                json_response = json.loads(re_llm_response)
                save_chat_history(user_id , query , llm_response) 
                return json_response
            except json.JSONDecodeError as e:
                if attempt < max_retries:
                    formatted_prompt += f"\nyour previous response was still invalid JSON which is {re_llm_response}, please provide the corrected JSON response"
                else:
                    # for attempt in max_retries:
                    json_response = {
                        "error" : "Invalid json response",
                        "origional_response" : re_llm_response
                    }
                    return json_response

if __name__ == "__main__":
    # response_json = get_ai_response(query="I feel unwell" , user_id="11221122") 
    while True:
        query = input("ask questions , type end to exit")
        if query == "end":
            break
        response_json = get_ai_response(query=query , user_id="98780266")
        print(response_json) 
    # get_ai_response(query="fewer",user_id=9878098)