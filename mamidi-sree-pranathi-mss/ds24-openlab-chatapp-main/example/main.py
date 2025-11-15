from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Inject custom CSS to hide Streamlit's default UI elements
def hide_streamlit_ui():
    st.markdown(
        """
        <style>
        header [data-testid="stToolbar"] {
            visibility: hidden;
        }
        footer {
            visibility: hidden;
        }
        header [data-testid="stHeader"] {
            visibility: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Initialize chat session
chat_session = None

# Function to get a response from the Gemini model
def get_gemini_response(user_prompt: str, model_name, temperature, top_p):
    global chat_session
    try:
        if chat_session is None:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction="system instruction"
            )
            chat_session = model.start_chat()

        generation_config = {
            "temperature": temperature,
            "top_p": top_p,
            "response_mime_type": "text/plain",
        }

        prompt = f"""
        You are an AI assistant. Your task is to understand and analyze input. 
        Your goal is to assist users interactively based on the following data:

        User's original request: {user_prompt}

        Your responses should be clear, concise, and accurate. Pull information from the diagram context if applicable. 
        If symbols, flows, or connections are mentioned, provide detailed explanations of their roles. 
        Maintain a structured approach for complex queries.
        """
        response = chat_session.send_message(prompt, generation_config=generation_config)
        return response.text

    except Exception as e:
        st.error(f"Error generating text: {str(e)}")
        return None

# Function to display chat history in Streamlit
def display_chat_history(chat_history):
    """Display chat history."""
    for message in chat_history:
        role = message["role"]
        content = message["content"]
        if role == "user":
            with st.chat_message("user"):
                st.markdown(f"**You:** {content}")
        elif role == "assistant":
            with st.chat_message("assistant"):
                st.markdown(f"**Assistant:** {content}")

# Main application logic
def main():
    hide_streamlit_ui()

    # App Title and Sidebar
    st.header("Gemini ChatApp Builder")
    dark_blue_html = """
        <div style="width: 100%; height: 4px; background-color: #00aae7; margin-top: -4px; border-radius: 3px;"></div>
        """
    st.markdown(dark_blue_html, unsafe_allow_html=True)

    st.logo("logos/miracle-logo-dark.png", size="large")
    st.image("logos/Digital_Summit_24_Logo_Dark.svg", width=80)
    css = """
        <style>
            [data-testid="stImage"] {
                width: 100px !important;
                position: fixed !important;
                top: 50px;  
                right: 80px;  
                z-index: 1000;
            }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)
    # st.sidebar.header("Settings", divider="blue")
    # Sidebar Header with Divider
    st.sidebar.markdown(
        """
        <style>
            .sidebar-header {
                font-size: 20px;
                font-weight: bold;
                color: #232527;
                margin-bottom: 10px;
                border-bottom: 3px solid #2368a0;
                padding-bottom: 5px;
            }
        </style>
        <div class="sidebar-header">Settings</div>
        """,
        unsafe_allow_html=True,
    )


    # Sidebar Styling with Light Blue
    st.sidebar.markdown(
        """
        <style>
            .sidebar-title {
                color:#00aae7;
                font-weight: bold;
            }
            .sidebar-input .stSlider, .sidebar-input .stNumberInput {
                color: #00aae7;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar Components
    st.sidebar.markdown('<div class="sidebar-title">Choose Model</div>', unsafe_allow_html=True)
    model_name = st.sidebar.selectbox(
        "",
        ["gemini-1.5-pro", "gemini-1.5-flash"]
    )
    st.sidebar.markdown('<div class="sidebar-title">Temperature</div>', unsafe_allow_html=True)
    temperature = st.sidebar.slider("", min_value=0.0, max_value=1.0, step=0.1, value=0.30)

    st.sidebar.markdown('<div class="sidebar-title">Top_P</div>', unsafe_allow_html=True)
    top_p = st.sidebar.number_input("", value=0.95)

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    st.markdown(
        """
        <style>
            .stButton > button {
                background-color:#ef4048;
                padding: 8px 25px;
                font-size: 16px;
                cursor: pointer;
                border-radius: 10px;
                font-weight: bold;
            }
            .stButton {
                text-align: right;
                margin-top: -50px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Clear the chat history
    if st.button("Reset", type="primary"):
        st.session_state.chat_history = []
        st.rerun()

    # Input box for user prompt
    user_input = st.chat_input("Type your message...")

    # Handle user input
    if user_input:
        # Add the user's question to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        display_chat_history(st.session_state.chat_history)

        # Show a spinner while processing the input
        with st.spinner("Processing..."):
            # Get response from the Gemini model
            response = get_gemini_response(user_input, model_name, temperature, top_p)
            if response:
                # Add the model's response to the chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

    # Always display the chat history after updates
    if st.session_state.chat_history:
        display_chat_history(st.session_state.chat_history)

if __name__ == "__main__":
    main()
