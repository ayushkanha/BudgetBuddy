from streamlit_option_menu import option_menu
import streamlit as st

# Set wide layout
st.set_page_config(page_title="Top Navbar", layout="wide")

# --- REMOVE TOP SPACE ---
st.markdown("""
    <style>
        
    </style>
""", unsafe_allow_html=True)
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
# with col2:
#     selected = option_menu(
#         menu_title=None,
#         options=["Settings", "Chat", "Mail"],
#         icons=["gear", "chat-left-text", "envelope"],
#         menu_icon="cast",
#         default_index=0,
#         orientation="horizontal",
#         styles={
#             "container": {"padding": "0!important", "background-color": "#0E1117"},
#             "icon": {"color": "white", "font-size": "20px"},
#             "nav-link": {"font-size": "18px", "text-align": "center", "margin": "0px", "--hover-color": "#262730"},
#             "nav-link-selected": {"background-color": "#1f6f78"},
#         }
#     )

# # --- PAGE CONTENT ---
# if selected == "Settings":
#     st.title("⚙️ Settings")
#     st.write("This is the Settings page.")
# elif selected == "Chat":
#     st.title("💬 Chat")
#     st.write("This is the Chat interface.")
# elif selected == "Mail":
#     st.title("📧 Mail")
#     st.write("This is the Mail inbox.")
# on = st.toggle("Voice Chat")
            
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
                "nav-link": {"font-size": "18px", "text-align": "center", "margin": "0px", "--hover-color": "#262730"},
                "nav-link-selected": {"background-color": "#1f6f78"},
            }
        )

if selected == "Chat":
    # Display chat history
    st.session_state.chat_history=[]
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if msg.get("type") == "image":
                st.image(msg["content"], caption=msg["content"])
            else:
                st.markdown(msg["content"])
    
    # Create a container for the chat input at the bottom

    st.write("") # Add some space
    on = st.toggle("Voice Chat")
    
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