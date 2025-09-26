# modules/a_guide.py
import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- CONFIGURATION ---
MENTORS_FILE = "data/mentors.csv"

# --- HELPER FUNCTIONS ---

def load_mentors():
    """Loads mentor profiles from the CSV file."""
    try:
        return pd.read_csv(MENTORS_FILE)
    except FileNotFoundError:
        st.error("The mentors.csv file was not found. Please create it in the 'data' folder.")
        return pd.DataFrame()

def configure_ai():
    """Configures the Generative AI model with the API key from secrets."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-pro')
    except (KeyError, ValueError):
        st.error("Gemini API Key is not configured. Please add it to your .streamlit/secrets.toml file.")
        return None

def generate_initial_question(model, mentor, problem):
    """Generates the first follow-up question from the selected mentor."""
    # This new prompt injects ALL the rich data from the CSV
    prompt = f"""
    You are role-playing as {mentor['mentor_name']}. Your persona is defined by the following attributes:
    - Core Philosophy: "{mentor['core_philosophy']}"
    - Communication Style: "{mentor['communication_style']}"
    - Mental Models & Frameworks: "{mentor['mental_models_and_frameworks']}"
    - Key Quotes that capture your voice: "{mentor['key_quotes']}"
    - What You Tell People to AVOID: "{mentor['anti_patterns_to_avoid']}"

    A user has come to you with the following situation: "{problem}"

    Based on your complete persona, ask one single, insightful, clarifying question to better understand the root of the user's problem.
    Draw upon your unique mental models and communication style.
    Do NOT offer any advice or solutions yet. Just ask the question.
    """
    response = model.generate_content(prompt)
    return response.text

def generate_advice(model, mentor, chat_history):
    """Generates the final advice based on the conversation history."""
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
    
    # This new prompt also injects all the rich data for context
    prompt = f"""
    You are role-playing as {mentor['mentor_name']}. Your persona is defined by the following attributes:
    - Core Philosophy: "{mentor['core_philosophy']}"
    - Communication Style: "{mentor['communication_style']}"
    - Mental Models & Frameworks: "{mentor['mental_models_and_frameworks']}"
    - Key Quotes that capture your voice: "{mentor['key_quotes']}"
    - What You Tell People to AVOID: "{mentor['anti_patterns_to_avoid']}"

    You have been having a conversation with a user. Here is the history of the conversation:
    {history_str}

    Based on your complete persona and the entire conversation:
    1.  Provide a concise, actionable piece of advice.
    2.  Incorporate one of your specific mental models or frameworks.
    3.  Make sure the advice helps the user avoid one of the anti-patterns.
    4.  Deliver the advice in your unique communication style.
    """
    response = model.generate_content(prompt)
    return response.text

# --- MAIN PAGE FUNCTION ---

def show_guide_page():
    st.title("The Guide")
    st.write("When you're stuck, seek counsel from your chosen mentors.")

    mentors_df = load_mentors()
    model = configure_ai()

    if model is None or mentors_df.empty:
        return # Stop execution if AI or mentors aren't loaded

    # Initialize session state for the conversation
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "mentor_selected" not in st.session_state:
        st.session_state.mentor_selected = None

    # Display the chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # --- Start a new session if there's no active conversation ---
    if not st.session_state.messages:
        st.subheader("Start a New Counsel Session")
        
        mentor_names = mentors_df['mentor_name'].tolist()
        chosen_mentor_name = st.selectbox("Choose your guide:", mentor_names)
        
        user_problem = st.text_area("Describe the situation you're facing:", height=150)
        
        if st.button("Seek Counsel"):
            if chosen_mentor_name and user_problem:
                # Find the selected mentor's profile
                st.session_state.mentor_selected = mentors_df[mentors_df['mentor_name'] == chosen_mentor_name].iloc[0]
                
                # Add user's initial problem to chat
                st.session_state.messages.append({"role": "user", "content": user_problem})
                
                # Generate the mentor's first question
                with st.spinner(f"Asking {chosen_mentor_name} for their thoughts..."):
                    initial_question = generate_initial_question(model, st.session_state.mentor_selected, user_problem)
                    st.session_state.messages.append({"role": "assistant", "content": initial_question})
                st.rerun() # Rerun to display the new chat messages
            else:
                st.warning("Please choose a mentor and describe your situation.")

    # --- Handle the ongoing conversation ---
    if prompt := st.chat_input("Your response..."):
        # Add user's new message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate the final advice (for this simple version, we'll get advice after one follow-up)
        with st.spinner("Formulating their advice..."):
            advice = generate_advice(model, st.session_state.mentor_selected, st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": advice})
        
        # Add a button to end the session
        st.session_state.messages.append({"role": "system", "content": "SESSION_END"})
        st.rerun()
    
    # --- Handle Session End ---
    if st.session_state.messages and st.session_state.messages[-1].get("content") == "SESSION_END":
        if st.button("Start a New Session"):
            # Clear the session state to reset the page
            st.session_state.messages = []
            st.session_state.mentor_selected = None
            st.rerun()