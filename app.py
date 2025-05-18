import streamlit as st
from datetime import date
from database import (
    init_db, register_user, verify_login, add_task, get_tasks,
    update_task_done, delete_task, get_due_tasks_today
)

# Initialize the database
init_db()

# Session state setup
if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None

def login_page():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_id = verify_login(username, password)
        if user_id:
            st.session_state.user_id = user_id
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid username or password")

def register_page():
    st.title("📝 Register")
    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")
    if st.button("Register"):
        success, msg = register_user(username, password)
        if success:
            st.success(msg + ". Please log in.")
        else:
            st.error(msg)

def todo_page():
    st.title(f"📋 {st.session_state.username}'s To-Do List")

    due_today = get_due_tasks_today(st.session_state.user_id)
    if due_today:
        st.warning(f"⚠️ Tasks due today: {', '.join(due_today)}")

    with st.form("add_task", clear_on_submit=True):
        desc = st.text_input("Task Description")
        due_date = st.date_input("Due Date", value=date.today())
        priority = st.slider("Priority", 0, 5, 2)
        category = st.selectbox("Category", ["Work", "Personal", "Health", "Study", "Other"])
        if st.form_submit_button("Add Task"):
            if desc.strip():
                add_task(st.session_state.user_id, desc.strip(), due_date.isoformat(), priority, category)
                st.success("Task added!")
                st.rerun()
            else:
                st.warning("Task description cannot be empty.")

    tasks = get_tasks(st.session_state.user_id)
    if not tasks:
        st.info("No tasks yet.")
    else:
        st.subheader("📅 Task List")
        for task_id, desc, done, due, priority, category in tasks:
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                label = f"{desc} | 📅 {due} | ⭐ {priority} | 🏷️ {category}"
                checked = st.checkbox(label, value=bool(done), key=f"check_{task_id}")
                if checked != bool(done):
                    update_task_done(task_id, int(checked))
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{task_id}"):
                    delete_task(task_id)
                    st.success("Task deleted!")
                    st.rerun()

    if st.button("🚪 Logout"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()

# Main flow
if st.session_state.user_id is None:
    page = st.sidebar.radio("Choose Page", ["Login", "Register"])
    if page == "Login":
        login_page()
    else:
        register_page()
else:
    todo_page()
