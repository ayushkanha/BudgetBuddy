from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
import re
import os
from spreedsheet import add_values,extract_values
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from langchain.prompts import PromptTemplate
from voice import text_to_speech,transcribe
from streamlit_option_menu import option_menu
from mail import mail
from setting import setting
import css

load_dotenv()
groq_key = os.getenv("Groq_API_KEY")
users = os.getenv("User_names").split(",")
passwords = os.getenv("Passwords").split(",")
user=""
llm = ChatGroq(model="llama-3.3-70b-versatile",groq_api_key=groq_key)

def user_information(input):

    if st.session_state.user_name != "":

        output= f"User Name = {st.session_state.user_name} , User email = {st.session_state.user_email},User Date Of birth = {st.session_state.user_date} , user Monthly budget = {st.session_state.budget}, user desiznation = {st.session_state.position}"
        return output
    else:
        return "ask user to fill information in setings so be get to know about them."
def append_to_sheet_input_string(input_string,):
    pattern = r"Date:\s*(.*?),\s*Type:\s*(.*?),\s*Category:\s*(.*?),\s*Amount:\s*(.*?),\s*Note:\s*(.*)"
    
    match = re.match(pattern, input_string)
    if match:
        date, tx_type, category, amount, note = match.groups()
        return add_values([date.strip(), tx_type.strip(), category.strip(), amount.strip(), note.strip()],user)
    else:
        raise ValueError("Input string format is invalid.")

value_adder_tool = Tool(
    name="GoogleSheetAppender",
    func=append_to_sheet_input_string,
    description=(
        "Append a new financial record to a Google Sheet with the format: "
        "'Date: <YYYY-MM-DD>, Type: <Income|Expense>, Category: <text>, Amount: <number>, Note: <text>'. "
        "Example: 'Date: 2025-05-17, Type: Expense, Category: Food, Amount: 500, Note: Dinner'. "
        "The data will be added as a new row to the sheet in this order: Date, Type, Category, Amount, Note."
    )

)
google_sheet_reader_tool = Tool(
    name="GoogleSheetReader",
    func=extract_values,
    description=(
        "Fetch all financial records from the Google Sheet. "
        "No input is needed. Use this to retrieve the full dataset for summarizing or analyzing finances."
    )
)
user_info=Tool(
    name="UserInformation",
    func=user_information,
    description=(
        "Fetch all general information about user. "
    ))
tools = [value_adder_tool,google_sheet_reader_tool,user_info]

st.set_page_config(page_title="BudgetBuddy",layout="centered")


st.markdown(
    """
    <style>
    /* Target the logo image in the sidebar */
    [alt="Logo"] {
        height: 70px; /* Adjust this to your desired height */
        width: auto;  /* Maintain aspect ratio */
        
    }
    .block-container {
            padding-top: 0rem;
        }
    header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)
col1, col2 = st.columns([1, 6])
with col1:
    st.logo("logo.png")
# --- NAVIGATION BAR ---



if "agent" not in st.session_state:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    st.session_state.agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True, 
        agent_kwargs={"system_message":f"""You are a financial assistant. The current date and time is: {now}.
                            Use this for interpreting relative dates like 'today', 'yesterday', or calculating time-based summaries.
                            Your job is to help users manage, track, and analyze their personal finances.

    You have access to tools that allow you to:
    - Log new financial transactions (income or expenses) to a Google Sheet
    - Retrieve past transactions to analyze spending patterns
    - Send important financial updates or summaries via email

    When the user provides new financial information (e.g., date, type, category, amount, and note), use the GoogleSheetAppender tool to save it in the correct format.

    If the user asks for a summary, analysis, or past records, use the appropriate tools to retrieve and interpret the data.

    Always guide the user with helpful financial insights such as:
    - Monthly spending habits
    - Expense category trends
    - Income vs. expense balance
    - Suggestions for budgeting or saving

    Keep your responses professional but friendly. Prioritize clarity and actionability. Use tools when necessary and do not make assumptions about the user's finances without checking the data.
    """}
    )
    st.session_state.chat_history = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    css.form()
    st.subheader("Login Page")
    st.markdown('<div class="form-style">', unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.session_state.user_date=""
        st.session_state.user_email=""
        st.session_state.user_name=""
        st.session_state.budget=""
        st.session_state.position=""

        user = st.text_input("Enter Username:")
        password = st.text_input("Enter your Password:", type="password")
        submitted = st.form_submit_button("Log in")
        
        if submitted:
            if user in users:
                if password == passwords[users.index(user)]:
                    st.success("Login successful")
                    st.session_state.logged_in = True
                    st.rerun()

                else:
                    st.error("Incorrect password")
            else:
                st.error("Incorrect username")
    st.markdown('</div>', unsafe_allow_html=True)
if not st.session_state.logged_in:
    login()
else:
    with col2:
        selected = option_menu(
            menu_title=None,
            options=["Chat", "Mail","Settings"],
            icons=["chat-left-text", "envelope","gear"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#0E1117"},
                "icon": {"color": "white", "font-size": "20px"},
                "nav-link": {"font-size": "18px", "text-align": "center", "margin": "0px", "--hover-color": "#204044"},
                "nav-link-selected": {"background-color": "#1f6f78"},
            }
        )
    if selected == "Settings":
        st.title("⚙️ Settings")
        setting()
    elif selected == "Chat":
        on = st.toggle("Voice Chat")
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                if msg.get("type") == "image":
                    st.image(msg["content"], caption=msg["content"])
                else:
                    st.markdown(msg["content"])
        
        # Create a container for the chat input at the bottom
       
        st.write("") # Add some space
        
        
        if on:
            uploaded_file = st.audio_input("Record a Voice Message")
            if uploaded_file and st.button('🎤 Confirm Audio'):
                user_input = transcribe(uploaded_file)
                if user_input:
                    # Show user message
                    st.chat_message("user").markdown(user_input)
                    st.session_state.chat_history.append({"role": "user", "content": user_input})

                    # Run agent
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            response = st.session_state.agent.run(user_input)
                            if response.strip():
                                audio_file = text_to_speech(response)
                                st.sidebar.audio(audio_file, format='audio/mp3', autoplay=True)
                            st.markdown(response)
                            st.session_state.chat_history.append({"role": "assistant", "content": response})
        else:
            user_input = st.chat_input("Ask something to the agent...")

            if user_input:
                # Show user message
                st.chat_message("user").markdown(user_input)
                st.session_state.chat_history.append({"role": "user", "content": user_input})

                # Run agent
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = st.session_state.agent.run({"input": user_input})
                        st.markdown(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                            
    elif selected == "Mail":
        st.title("📧 Mail")
        mail()