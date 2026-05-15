import streamlit as st
from groq import Groq

st.markdown("""
    <style>
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Moves the + button into the text bar area */
    .stPopover {
        position: fixed;
        bottom: 34px;
        left: 20px;
        z-index: 1000;
    }
    .stPopover > button {
        border-radius: 10px !important;
        width: 35px !important;
        height: 35px !important;
        background-color: #262730 !important;
        border: 1px solid #464b5d !important;
        font-weight: bold !important;
        color: white !important;
    }
    /* Pushes text input to the right to make room for [+] */
    .stChatInputContainer > div {
        margin-left: 45px !important;
    }
    </style>
    """, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

with st.sidebar:
    st.header("Chats")
    if st.button("➕ New Chat"):
        new_name = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_name] = []
        st.session_state.current_chat = new_name
        st.rerun()
    st.divider()
    for chat_name in st.session_state.all_chats.keys():
        if st.button(chat_name):
            st.session_state.current_chat = chat_name
            st.rerun()

messages = st.session_state.all_chats[st.session_state.current_chat]

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.popover("+"):
    img_file = st.file_uploader("🖼Select image", type=['png', 'jpg', 'jpeg'])
    doc_file = st.file_uploader("📁Select file")

prompt = st.chat_input("Say hello!")

if prompt:
    context_info = ""
    if doc_file:
        try:
            file_content = doc_file.getvalue().decode("utf-8")
            context_info = f"\n\n[File Content from {doc_file.name}]:\n{file_content}"
        except:
            context_info = f"\n\n[Attached File: {doc_file.name}]"
    
    if img_file:
        context_info += f"\n\n[User attached an image: {img_file.name}. Note: I cannot see the image content yet, only the name.]"

    full_prompt = prompt + context_info
    messages.append({"role": "user", "content": full_prompt})
    st.rerun()

if messages and messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": m["role"], "content": m["content"]} for m in messages]
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            messages.append({"role": "assistant", "content": res})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
