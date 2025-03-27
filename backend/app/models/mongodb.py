import os
from pymongo import MongoClient
from dotenv import load_dotenv
from langchain_groq import ChatGroq 

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["Langchain_user_history"]
history_collection = db["user_conversation"]

# Initialize llm
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=1024,
    timeout=10,
    max_retries=2,
)

def get_summary(text):
    # Fetch summary from MongoDB
    llm_inp = "Summarize below content upto max 5 lines ,do not unnecessary words or sentences , if there is already any summary also consider that function \n" + text
    summary = llm.invoke(llm_inp).content
    summary = "Summary of previous conversation : " + summary
    return summary


def save_chat_history(user_id: str, query: str, response: str):
    """Save user chat history to MongoDB"""
    existing_chat = history_collection.find_one({"user_id": user_id})
    
    if existing_chat:
        print("Length of conversation is : ", len(existing_chat["conversation"].split("\n")))
        if len(existing_chat["conversation"].split("\n")) >= 20 :
            # breakpoint()
            # Filter previous messages when conversation becomes above 40 and summarize it
            total_conversation_len = len(existing_chat["conversation"].split("\n")) + 2 # 2 for the new query and response
            summarize_conv_len = total_conversation_len - 40
            summzarize_inp = "\n".join(existing_chat["conversation"].split("\n")[:summarize_conv_len])
            
            summzarize_content = get_summary(summzarize_inp)
            updated_conversation = existing_chat["conversation"]
            updated_conversation += f"\nUser: {query}\nAI: {response}"
            updated_conversation = "\n".join(updated_conversation.split("\n")[-40:])
            updated_conversation = summzarize_content + f"\n{updated_conversation}"
            print(updated_conversation.split("\n") , len(updated_conversation.split("\n")))
            history_collection.update_one(
                {"user_id": user_id},
                {"$set": {"conversation": updated_conversation}}
            )
        else :
            # If user exists, update conversation
            updated_conversation = existing_chat["conversation"]
            updated_conversation += f"\nUser: {query}\nAI: {response}"
            history_collection.update_one(
                {"user_id": user_id},
                {"$set": {"conversation": updated_conversation}}
            )
    else:
        # If user does not exist, create a new entry
        chat_entry = {
            "user_id": user_id,
            "conversation": f"User: {query}\nAI: {response}"
        }
        history_collection.insert_one(chat_entry)

def get_chat_history(user_id: str):
    """Retrieve user chat history from MongoDB"""
    history = history_collection.find_one({"user_id": user_id})
    if not history:
        return None
    return history["conversation"]

def clear_chat_history(user_id: str):
    """Delete chat history for a user"""
    history_collection.delete_many({"user_id": user_id})

# save_chat_history("212" , "hello" , "hi") 
