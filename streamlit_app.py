import streamlit as st
from groq import Groq
import base64

st.markdown("""
    <style>
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}

    .stPopover {
        position: fixed;
        bottom: 34px;
        left: 20px;
        z-index: 1000;
    }
    .stPopover > button {
        border-radius: 10px !important;
        width: 42px !important;
        height: 42px !important;
        background-color: #262730 !important;
        border: 1px solid #464b5d !important;
        font-weight: bold !important;
        color: white !important;
        font-size: 18px !important;
    }
    .stChatInputContainer > div {
        margin-left: 55px !important;
    }
    div[data-testid="stPopoverBody"] {
        bottom: 80px !important;
        top: auto !important;
        left: 10px !important;
        position: fixed !important;
    }
    </style>
""", unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"
if "pending_image_b64" not in st.session_state:
    st.session_state.pending_image_b64 = None
if "pending_doc_text" not in st.session_state:
    st.session_state.pending_doc_text = None

with st.sidebar:
    st.header("Chats")
    if st.button("New Chat"):
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
        if message.get("image_b64"):
            st.image(base64.b64decode(message["image_b64"]))
        st.markdown(message["content"])

if st.session_state.pending_image_b64:
    st.info("Image attached — send your message!")
if st.session_state.pending_doc_text:
    st.info("File attached — send your message!")

with st.popover("➕"):
    st.markdown("**Attach**")
    img_file = st.file_uploader("Image", type=["png", "jpg", "jpeg"], key="img_uploader")
    doc_file = st.file_uploader("File", key="doc_uploader")
    if img_file:
        img_bytes = img_file.read()
        st.session_state.pending_image_b64 = base64.b64encode(img_bytes).decode("utf-8")
        st.success("Image ready!")
    if doc_file:
        try:
            st.session_state.pending_doc_text = f"[File: {doc_file.name}]\n{doc_file.getvalue().decode('utf-8')}"
        except:
            st.session_state.pending_doc_text = f"[Attached file: {doc_file.name}]"
        st.success("File ready!")

prompt = st.chat_input("Say hello!")

if prompt:
    image_b64 = st.session_state.pending_image_b64
    context_info = st.session_state.pending_doc_text or ""

    if image_b64:
        user_msg_api = {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                {"type": "text", "text": prompt + ("\n\n" + context_info if context_info else "")}
            ]
        }
    else:
        user_msg_api = {"role": "user", "content": prompt + ("\n\n" + context_info if context_info else "")}

    messages.append({
        "role": "user",
        "content": prompt + ("\n\n" + context_info if context_info else ""),
        "image_b64": image_b64
    })

    st.session_state.pending_image_b64 = None
    st.session_state.pending_doc_text = None
    st.rerun()

if messages and messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        try:
            api_messages = []
            for i, m in enumerate(messages):
                if m.get("image_b64") and i == len(messages) - 1:
                    api_messages.append({
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{m['image_b64']}"}},
                            {"type": "text", "text": m["content"]}
                        ]
                    })
                else:
                    api_messages.append({"role": m["role"], "content": m["content"]})

            model = "meta-llama/llama-4-scout-17b-16e-instruct" if messages[-1].get("image_b64") else "llama-3.3-70b-versatile"

            completion = client.chat.completions.create(model=model, messages=api_messages)
            res = completion.choices[0].message.content
            st.markdown(res)
            messages.append({"role": "assistant", "content": res})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
