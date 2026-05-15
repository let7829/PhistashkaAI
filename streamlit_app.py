import streamlit as st
from groq import Groq
import base64

st.markdown("""
    <style>
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}

    /* Hide default Streamlit file uploaders */
    [data-testid="stFileUploader"] { display: none; }

    .stChatInputContainer > div {
        margin-left: 0px !important;
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
if "pending_image_name" not in st.session_state:
    st.session_state.pending_image_name = None

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
        if message.get("image_b64"):
            st.image(base64.b64decode(message["image_b64"]))
        st.markdown(message["content"])

# --- File uploaders (hidden via CSS, triggered by JS buttons) ---
img_file = st.file_uploader("image", type=["png", "jpg", "jpeg"], key="img_uploader", label_visibility="collapsed")
doc_file = st.file_uploader("doc", key="doc_uploader", label_visibility="collapsed")

# --- Custom bottom bar with [+] menu ---
st.markdown("""
    <style>
    .upload-bar {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 10px;
        background: #262730;
        border: 1px solid #464b5d;
        border-radius: 12px;
        margin-bottom: 6px;
    }
    .upload-btn {
        background: #464b5d;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 5px 11px;
        cursor: pointer;
        font-size: 16px;
    }
    .upload-btn:hover { background: #5a6080; }
    </style>
    <div class="upload-bar">
        <button class="upload-btn" onclick="document.querySelector('[data-testid=stFileUploader] input[type=file]').click()">+</button>
        <button class="upload-btn" onclick="document.querySelectorAll('[data-testid=stFileUploader] input[type=file]')[1].click()">📁</button>
    </div>
""", unsafe_allow_html=True)

prompt = st.chat_input("Say hello!")

# Store uploaded image as base64 in session
if img_file:
    img_bytes = img_file.read()
    st.session_state.pending_image_b64 = base64.b64encode(img_bytes).decode("utf-8")
    st.session_state.pending_image_name = img_file.name

if prompt:
    image_b64 = st.session_state.pending_image_b64
    image_name = st.session_state.pending_image_name
    context_info = ""

    if doc_file:
        try:
            context_info = f"\n\n[File: {doc_file.name}]:\n{doc_file.getvalue().decode('utf-8')}"
        except:
            context_info = f"\n\n[Attached File: {doc_file.name}]"

    # Build user message
    if image_b64:
        # Use vision-capable model when image is present
        user_msg_api = {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_b64}"
                    }
                },
                {
                    "type": "text",
                    "text": prompt + context_info
                }
            ]
        }
    else:
        user_msg_api = {"role": "user", "content": prompt + context_info}

    # Store in chat history (text only for history display)
    messages.append({
        "role": "user",
        "content": prompt + context_info,
        "image_b64": image_b64
    })

    # Clear pending image
    st.session_state.pending_image_b64 = None
    st.session_state.pending_image_name = None

    st.rerun()

if messages and messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        try:
            # Build API messages — inject vision message for last user turn if it had an image
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

            completion = client.chat.completions.create(
                model=model,
                messages=api_messages
            )
            res = completion.choices[0].message.content
            st.markdown(res)
            messages.append({"role": "assistant", "content": res})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
