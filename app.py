# App.py
import streamlit as st
from modules import a_guide, b_path

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="The Compass",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- MAIN APP LOGIC ---

def main():
    """
    Main function to run the Streamlit application.
    It handles page navigation and calls the appropriate module.
    """
    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.title("🧭 The Compass")
        st.write("Your personal tool for direction and productivity.")
        
        # Using a radio button for navigation
        page_choice = st.radio(
            "Choose your module:",
            ("The Path", "The Guide"),
            label_visibility='collapsed' # Hides the label "Choose your module:"
        )
        
        st.info("Built with Streamlit by you!")

    # --- PAGE ROUTING ---
    # Load the selected page's content by calling its function
    if page_choice == "The Path":
        b_path.show_path_page()
        
    elif page_choice == "The Guide":
        a_guide.show_guide_page()

if __name__ == "__main__":
    main()

