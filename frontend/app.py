import streamlit as st
import requests

# API Base URL
API_URL = "http://127.0.0.1:8000/chat"

# Static User ID (can be enhanced with authentication later)
USER_ID = "212321"

# Initialize session state variables
if "stage" not in st.session_state:
    st.session_state.stage = "symptom_input"  # Possible stages: symptom_input, question, diagnosis
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "options" not in st.session_state:
    st.session_state.options = None
if "disease" not in st.session_state:
    st.session_state.disease = None
if "advice" not in st.session_state:
    st.session_state.advice = None

# Title
st.title("🩺 DiagnoAI - AI Health Chat")

# Stage 1: Symptom Input
if st.session_state.stage == "symptom_input":
    symptom = st.text_input("Please enter your symptoms below:", placeholder="e.g., fever, headache")
    
    if st.button("Submit Symptoms"):
        if symptom.strip():  # Ensure non-empty input
            with st.spinner("Processing your symptoms..."):
                try:
                    response = requests.post(API_URL, json={"user_id": USER_ID, "query": symptom})
                    response.raise_for_status()  # Raise exception for bad status codes
                    ai_response = response.json()["response"]

                    # Handle the two possible JSON formats
                    if "Question" in ai_response and "Options" in ai_response:
                        st.session_state.current_question = ai_response["Question"]
                        st.session_state.options = ai_response["Options"]
                        st.session_state.stage = "question"
                    elif "Disease" in ai_response and "Advice" in ai_response:
                        st.session_state.disease = ai_response["Disease"]
                        st.session_state.advice = ai_response["Advice"]
                        st.session_state.stage = "diagnosis"
                except requests.RequestException as e:
                    st.error(f"Error contacting the API: {e}")
                except KeyError:
                    st.error("Unexpected response format from API.")
        else:
            st.warning("Please enter your symptoms before submitting.")

# Stage 2: Follow-up Questions with Options
elif st.session_state.stage == "question":
    st.write(f"**{st.session_state.current_question}**")
    
    # Display radio buttons for options
    selected_option = st.radio(
        "Select one option:",
        st.session_state.options,
        index=None,  # No default selection
        key=f"radio_{st.session_state.current_question}"  # Unique key to avoid conflicts
    )
    
    if st.button("Submit Answer"):
        if selected_option:  # Ensure an option is selected
            with st.spinner("Analyzing your answer..."):
                try:
                    response = requests.post(API_URL, json={"user_id": USER_ID, "query": selected_option})
                    response.raise_for_status()
                    ai_response = response.json()["response"]

                    # Handle the next response
                    if "Question" in ai_response and "Options" in ai_response:
                        st.session_state.current_question = ai_response["Question"]
                        st.session_state.options = ai_response["Options"]
                        # Stage remains "question"
                    elif "Disease" in ai_response and "Advice" in ai_response:
                        st.session_state.disease = ai_response["Disease"]
                        st.session_state.advice = ai_response["Advice"]
                        st.session_state.stage = "diagnosis"
                except requests.RequestException as e:
                    st.error(f"Error contacting the API: {e}")
                except KeyError:
                    st.error("Unexpected response format from API.")
        else:
            st.warning("Please select an option before submitting.")

# Stage 3: Display Diagnosis
elif st.session_state.stage == "diagnosis":
    st.subheader("🩺 Diagnosis Result")
    st.success(f"**Disease:** {st.session_state.disease}")
    st.info(f"**Advice:** {st.session_state.advice}")