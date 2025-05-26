import streamlit as st
import datetime 
import css 
def setting():
    css.form()
    st.title("User Information Form")
    st.write("Please enter the required details below.")

    st.header("Enter Your Details")

    with st.form("user_info_form"):
        user_name = st.text_input(
            "Full Name",
            placeholder="e.g., John Doe" if st.session_state.user_name == "" else st.session_state.user_name ,
            help="Enter the full name of the user."
        )
        user_email = st.text_input(
            "Email Address",
            placeholder="e.g., john.doe@example.com" if st.session_state.user_email == "" else st.session_state.user_email,
            help="Enter the user's email address. This should be a valid email."
        )
        
        user_date = st.date_input("Date Of Birth", value=None)
        Gender = st.selectbox(
            "How would you like to be contacted?",
            ("Male", "Female", "Others"),
        )
        Position = st.text_input(
            "Your Degignation",
            placeholder="e.g., Doctor",
            help="Enter Your Degignation."
        )
        Budget = st.text_input(
            "Monthly Budget",
            placeholder="e.g., 50000" if st.session_state.budget == "" else st.session_state.budget
        )
        st.markdown('<div class="center-button">', unsafe_allow_html=True)
        submitted = st.form_submit_button("Submit Information")
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted:
            
            if not user_name:
                st.error("Name cannot be empty. Please enter a name.")
            elif not user_email or "@" not in user_email or "." not in user_email:
                st.error("Please enter a valid email address.")
            else:
                if user_date and user_email and user_name and Budget and Position :

                    st.session_state.user_date=user_date
                    st.session_state.user_email=user_email
                    st.session_state.user_name=user_name
                    st.session_state.budget=Budget
                    st.session_state.position=Position
                    st.toast('Data successfully stored',icon="🔔")
                else:
                    st.error("Please Enter all The data.")