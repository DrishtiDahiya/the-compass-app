# modules/b_path.py
import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
DATA_FILE = "data/tasks.csv"

# --- HELPER FUNCTIONS ---

def load_tasks():
    """Loads tasks from the CSV file into a pandas DataFrame."""
    try:
        # Load the CSV, ensuring 'due_date' is parsed as a datetime object
        df = pd.read_csv(DATA_FILE, parse_dates=['due_date'])
    except FileNotFoundError:
        # If the file doesn't exist, create an empty DataFrame with the correct columns
        df = pd.DataFrame(columns=['task_name', 'due_date', 'status'])
    return df

def save_tasks(df):
    """Saves the DataFrame back to the CSV file."""
    df.to_csv(DATA_FILE, index=False)

def get_countdown_str(due_date):
    """Generates a human-readable string for the time remaining until the due date."""
    delta = due_date.date() - datetime.now().date()
    days_left = delta.days
    
    if days_left < 0:
        return f"🔴 Overdue by {-days_left} day(s)"
    elif days_left == 0:
        return "🔵 Due Today"
    elif days_left == 1:
        return "🟡 Due Tomorrow"
    else:
        return f"⚪ Due in {days_left} days"

# --- MAIN PAGE FUNCTION ---

def show_path_page():
    """Displays the 'Path' page content for task management."""
    st.title("The Path")
    st.write("Your personal workflow and deadline tracker.")
    
    # Load the tasks from the CSV file
    tasks_df = load_tasks()
    
    # --- ADD A NEW TASK ---
    st.subheader("Add a New Task")
    with st.form("new_task_form", clear_on_submit=True):
        new_task_name = st.text_input("Task Name:", placeholder="e.g., Finalize the project report")
        new_task_due_date = st.date_input("Due Date:")
        
        submitted = st.form_submit_button("Add Task")
        
        if submitted:
            if new_task_name:
                # Create a new DataFrame for the new task
                new_task = pd.DataFrame([{
                    'task_name': new_task_name,
                    'due_date': pd.to_datetime(new_task_due_date),
                    'status': 'Active'
                }])
                
                # Concatenate the new task with the existing tasks
                tasks_df = pd.concat([tasks_df, new_task], ignore_index=True)
                save_tasks(tasks_df)
                st.success("Task added successfully!")
            else:
                st.warning("Please enter a task name.")

    st.divider()

    # --- DISPLAY ACTIVE TASKS ---
    st.subheader("Your Active Tasks")
    active_tasks = tasks_df[tasks_df['status'] == 'Active'].sort_values(by='due_date')

    if active_tasks.empty:
        st.info("You have no active tasks. Add one above!")
    else:
        for index, row in active_tasks.iterrows():
            col1, col2 = st.columns([0.05, 0.95])
            with col1:
                # Create a checkbox. The `key` is crucial for Streamlit to track its state.
                is_done = st.checkbox("", key=f"task_{index}")
            with col2:
                # Display the task name and its countdown string
                st.write(f"**{row['task_name']}**")
                st.caption(get_countdown_str(row['due_date']))
            
            # If the checkbox is ticked, update the status and rerun the app
            if is_done:
                tasks_df.loc[index, 'status'] = 'Done'
                save_tasks(tasks_df)
                st.rerun() # Rerun the script to refresh the view immediately

    # --- DISPLAY COMPLETED TASKS (in an expander) ---
    with st.expander("View Completed Tasks"):
        completed_tasks = tasks_df[tasks_df['status'] == 'Done']
        if completed_tasks.empty:
            st.write("No tasks completed yet.")
        else:
            for index, row in completed_tasks.iterrows():
                st.success(f"~~{row['task_name']}~~ - Completed on {row['due_date'].strftime('%Y-%m-%d')}")