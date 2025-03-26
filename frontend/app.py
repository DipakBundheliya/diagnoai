import streamlit as st
import requests

# API Base URL
API_URL = "http://127.0.0.1:8000/chat"

# Static User ID (In future, implement authentication)
USER_ID = "13121412"

# Initialize session state variables
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "options" not in st.session_state:
    st.session_state.options = None
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None
if "completed" not in st.session_state:
    st.session_state.completed = False

st.title("🩺 DiagnoAI - AI Health Chat")

# **Step 1: Initial Symptom Entry**
if not st.session_state.current_question and not st.session_state.completed:
    symptom = st.text_input("Enter your symptoms:")
    if st.button("Start Diagnosis"):
        if symptom:
            response = requests.post(API_URL, json={"user_id": USER_ID, "query": symptom})
            if response.status_code == 200:
                ai_response = response.json()["response"]

                # Check if it's a question or final diagnosis
                if "Question" in ai_response and "Options" in ai_response:
                    st.session_state.current_question = ai_response["Question"]
                    st.session_state.options = ai_response["Options"]
                    st.session_state.selected_option = None  # Reset selected option
                elif "Disease" in ai_response and "Advice" in ai_response:
                    st.session_state.completed = True
                    st.session_state.disease = ai_response["Disease"]
                    st.session_state.advice = ai_response["Advice"]
            else:
                st.error("Error contacting AI. Please try again.")

# **Step 2: Follow-up Question & Options (Only if Question Exists)**
if st.session_state.current_question and not st.session_state.completed:
    st.write(f"**{st.session_state.current_question}**")
    
    # Let user select an option but don't change immediately
    st.session_state.selected_option = st.radio(
        "Select an option:",
        st.session_state.options,
        index=None,  # Allow user to make a choice without default selection
        key="selected_radio"
    )
    
    if st.button("Submit Answer") and st.session_state.selected_option:
        response = requests.post(API_URL, json={"user_id": USER_ID, "query": st.session_state.selected_option})
        
        if response.status_code == 200:
            ai_response = response.json()["response"]
            
            # If AI asks another question
            if "Question" in ai_response and "Options" in ai_response:
                st.session_state.current_question = ai_response["Question"]
                st.session_state.options = ai_response["Options"]
                st.session_state.selected_option = None  # Reset selected option
            # If AI provides a diagnosis
            elif "Disease" in ai_response and "Advice" in ai_response:
                st.session_state.completed = True
                st.session_state.disease = ai_response["Disease"]
                st.session_state.advice = ai_response["Advice"]
                st.session_state.current_question = None  # End the chat
        else:
            st.error("Error contacting AI. Please try again.")

# **Step 3: Show Diagnosis Result**
if st.session_state.completed:
    st.subheader("🩺 Diagnosis Result")
    st.success(f"**Disease:** {st.session_state.disease}")
    st.info(f"**Advice:** {st.session_state.advice}")
