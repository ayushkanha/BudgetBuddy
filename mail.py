import streamlit as st
import datetime # Used for the date input default value
import css
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from spreedsheet import extract_values_between_dates
import re
from mailsender import send_email
import os 
from dotenv import load_dotenv
load_dotenv()
Google_API_KEY = os.getenv("Google_API_KEY")

def mail():
    llm_mail =  ChatGoogleGenerativeAI(
                        model="gemini-2.0-flash-lite",
                        temperature=0.7,
                        google_api_key=Google_API_KEY
                    )
    css.form()
    st.title("Finace Statment Form")
    st.write("Please enter the required details below.")

    # --- Input Form ---
    st.header("Enter Your Details")

    with st.form("user_info_form"):
        # Name Input
        user_name = st.text_input(
            "Full Name",
            placeholder="e.g., John Doe",
            help="Enter the full name of the user."
        )

        # Email Input
        user_email = st.text_input(
            "Email Address",
            placeholder="e.g., john.doe@example.com",
            help="Enter the user's email address. This should be a valid email."
        )
        
        user_date1 = st.date_input("Enter from when do you need data ", value=None)
        user_date2 = st.date_input("To", value=None)
        details = st.selectbox(
            "How much Details do you need?",
            ("In detail","Middle", "Summary" ),
        )
        submitted = st.form_submit_button("Submit Information")
        

        if submitted:
            
            if not user_name:
                st.error("Name cannot be empty. Please enter a name.")
            elif not user_email or "@" not in user_email or "." not in user_email:
                st.error("Please enter a valid email address.")
            else:
                if user_date1 and user_date2 and user_email and user_name and details :
                    st.success("Information submitted successfully!")
                    st.write("---")
                    st.subheader("Submitted Details:")
                    st.write(f"**Name:** {user_name}")
                    st.write(f"**Email:** {user_email}")
                    st.write(f"**Date:** {user_date1.strftime('%Y-%m-%d')}")
                    st.write(f"**Date:** {user_date2.strftime('%Y-%m-%d')}") 
                    
                    
                    
                    google_sheet_reader_tool = Tool(
                        name="GoogleSheetReader",
                        func=extract_values_between_dates,
                        description=(
                            "Extracts data from a Google Sheet, filtering rows based on a date column between specified start and end dates."
                            
                        )
                    )
                    

                    def send_email_input_string(input_string: str):
                        try:
                            # Regex for each part with non-greedy matching
                            to_match = re.search(r"to:\s*(.*?)(?=, subject:|$)", input_string, re.IGNORECASE)
                            subject_match = re.search(r"subject:\s*(.*?)(?=, message:|$)", input_string, re.IGNORECASE)
                            message_match = re.search(r"message:\s*(.*)", input_string, re.IGNORECASE | re.DOTALL)

                            to = to_match.group(1).strip() if to_match else None
                            subject = subject_match.group(1).strip() if subject_match else None
                            message = message_match.group(1).strip() if message_match else None

                            if message:
                                message = message.replace("\\n", "\n").replace("\\t", "\t")

                            if to and subject and message:
                                return send_email(to, subject, message)
                            else:
                                return "Error: Missing to, subject, or message."
                        except Exception as e:
                            return f"Error parsing input: {str(e)}"

                    email_tool = Tool(
                        name="EmailSender",
                        func=send_email_input_string,
                        description="Send an email. Format: 'to: <email>, subject: <subject>, message: <message>'."
                    )

                    tools = [email_tool, google_sheet_reader_tool]
                    
                    agent = initialize_agent(
                        tools=tools,
                        llm=llm_mail,
                        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                        verbose=True,
                        handle_parsing_errors=True
                    )

                    # prompt = (
                    #     f"The user {user_name} wants a {details} financial report from {user_date1} to {user_date2}. "
                    #     f"Fetch the data using GoogleSheetReader, generate the report, and send it via EmailSender "
                    #     f"to: {user_email}, subject: 'Your Financial Report', message: <include the generated report here>."
                    # )
                    prompt = f"""
                        You are an intelligent assistant helping to generate and send financial reports.

                        1. Use the `GoogleSheetReader` tool to retrieve all financial data.
                        2. Filter the data from {user_date1} to {user_date2}.
                        3. Based on the user's preference, prepare a {details} report:
                        - **Summary** should group totals by category and show income vs. expenses.
                        - **Detailed** should list each transaction in a clean format.
                        4. Add a brief analytics insight such as top spending category or spending trend.
                        5. Compose a well-formatted email body for the user {user_name}.
                        6. Use the `EmailSender` tool to send the report with:
                        to: {user_email}
                        subject: Financial Report ({user_date1} to {user_date2})
                        message: <insert the report text here>

                        Respond only using the tools and follow this workflow strictly.
                        """
                    
                    with st.status("Sending Mail..."):
                        responce=agent.run(prompt)
                    

                    st.toast(responce,icon="🔔")
