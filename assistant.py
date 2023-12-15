import openai
import requests
import streamlit as st
import time
import function_hanlders
from assistant_methods import client

openai_api_key = "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"
assistant_id = 'asst_e6Qo3qLTXm5TjFjrzFgpP7bY'


# Initialize the OpenAI client


def files():
    uploaded_files = st.sidebar.file_uploader("Choose a file", accept_multiple_files=True, key="file_uploader")
    if uploaded_files:
        if "uploaded_files" not in st.session_state:
            st.session_state.uploaded_files = []

        for uploaded_file in uploaded_files:
            if uploaded_file not in st.session_state.uploaded_files:
                st.session_state.uploaded_files.append(uploaded_file)


def show_uploaded_files():
    if "uploaded_file_names" in st.session_state and st.session_state.uploaded_file_names:
        st.sidebar.write("Uploaded Files:")
        to_remove = []
        for file_idx, file_name in enumerate(st.session_state.uploaded_file_names):
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                st.write(file_name)
            with col2:
                if st.button('Remove', key=f'remove_{file_idx}'):
                    to_remove.append(file_idx)

        # Remove selected files
        for idx in reversed(to_remove):  # Reverse to avoid index shifting
            st.session_state.uploaded_file_names.pop(idx)
    else:
        st.sidebar.write("No files uploaded yet.")


def initialize_streamlit_state():
    if "file_id_list" not in st.session_state:
        st.session_state.file_id_list = []
    if "start_chat" not in st.session_state:
        st.session_state.start_chat = False
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "uploaded_file_names" not in st.session_state:
        st.session_state.uploaded_file_names = []  # Initialize the uploaded_file_names list
    if "messages" not in st.session_state:
        st.session_state.messages = []


def fetch_image(file_id):
    """
    Fetches an image from the OpenAI API using the given file ID.
    """
    # URL for fetching file content from OpenAI
    url = f"https://api.openai.com/v1/files/{file_id}/content"

    # Request headers with authentication
    headers = {
        "Authorization": f"Bearer {openai.api_key}"
    }

    # Make the GET request to fetch the image
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the image content
        return response.content
    else:
        # Handle errors (e.g., log them, return None, raise an exception)
        print(f"Failed to fetch image: {response.status_code} - {response.text}")
        return None


class InvestmentAdvisor:
    def __init__(self):
        self.client = client
        self.assistant_id = assistant_id
        initialize_streamlit_state()
        self.start_chat_session()

    def start_chat_session(self):
        st.session_state.start_chat = True
        thread = self.client.beta.threads.create()
        st.session_state.thread_id = thread.id
        st.sidebar.write("### Commands")
        st.sidebar.write("Watchlist Management")
        st.sidebar.write("Analyzing Trading Opportunities")
        st.sidebar.write("Order Management")
        st.sidebar.write("Review and Adjustment")
        st.sidebar.write("Stock Research and Selection (Extended Functions)")

    def process_user_message(self, prompt):
        # Add user message to the state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Add the user's message to the existing thread
        self.client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Create a run with additional instructions
        run = self.client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=self.assistant_id,
            instructions="Please answer the queries using the knowledge provided in the files. Mark additional information clearly with a different color."
        )

        # Poll for the run to complete and retrieve the assistant's messages
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )

            if run_status.status == "requires_action":
                function_hanlders.handle_required_action(st.session_state.thread_id, run.id, run_status.required_action)
            elif run_status.status == "completed":
                self.display_assistant_messages(run)
                break
            elif run_status.status in ['queued', 'in_progress']:
                with st.empty():
                    st.write(f"Run status: {run_status.status}. Waiting...")
                    time.sleep(10)
                    st.write('')
            if run_status.status in ['cancelled', 'failed', 'expired']:
                st.error(f"Run {run_status.status}. Please try again.")
                break

    def display_assistant_messages(self, run):
        # Display existing messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Fetch new messages from the assistant related to the specific run
        new_messages = self.client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Display new assistant messages
        full_response = ""
        for message in new_messages:
            if message.run_id == run.id and message.role == "assistant":
                for content in message.content:
                    if hasattr(content, 'text'):
                        full_response = content.text.value
                        with st.chat_message("assistant"):
                            st.markdown(full_response, unsafe_allow_html=True)
                    elif hasattr(content, 'image_file'):
                        file_id = content.image_file.file_id
                        image = fetch_image(file_id)
                        if image:
                            with st.chat_message("assistant"):
                                st.image(image, caption="Image from Assistant")

        # Append the full response of new messages to the session state
        if full_response:
            st.session_state.messages.append({"role": "assistant", "content": full_response})
