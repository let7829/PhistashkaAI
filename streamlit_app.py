import streamlit as st
from groq import Groq
import base64
import random
from datetime import datetime

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Phistashka AI")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .lightbox {
        display: none;
        position: fixed;
        z-index: 9999;
        left: 0;
        top: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(0,0,0,0.9);
    }
    .lightbox:target {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .lightbox img {
        max-width: 95%;
        max-height: 95%;
        object-fit: contain;
    }
    .close-btn {
        position: absolute;
        top: 20px;
        left: 20px;
        color: white;
        font-size: 40px;
        text-decoration: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Phistashka AI")

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

with st.sidebar:
    st.header("Chats")
    if st.button("➕ New Chat"):
        new_name = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_name] = []
        st.session_state.current_chat = new_name
        st.rerun()
    
    st.divider()
    for chat_name in st.session_state.all_chats.keys():
        if st.button(chat_name, key=f"select_{chat_name}"):
            st.session_state.current_chat = chat_name
            st.session_state.edit_index = None
            st.rerun()

messages = st.session_state.all_chats[st.session_state.current_chat]

for i, message in enumerate(messages):
    role = message["role"]
    if role == "user":
        col_btns, col_txt = st.columns([0.15, 0.85])
        with col_btns:
            if st.button("✏️", key=f"edit_{i}"):
                st.session_state.edit_index = i
                st.rerun()
            if st.button("↩️", key=f"undo_{i}"):
                st.session_state.all_chats[st.session_state.current_chat] = messages[:i]
                st.rerun()
        with col_txt:
            with st.chat_message("user"):
                content = message["content"]
                if st.session_state.edit_index == i:
                    text_val = content[0]["text"] if isinstance(content, list) else content
                    edit_val = st.text_input("Edit:", value=text_val, key=f"input_{i}")
                    if st.button("Save", key=f"save_{i}"):
                        if isinstance(content, list):
                            content[0]["text"] = edit_val
                            messages[i]["content"] = content
                        else:
                            messages[i]["content"] = edit_val
                        st.session_state.all_chats[st.session_state.current_chat] = messages[:i+1]
                        st.session_state.edit_index = None
                        st.rerun()
                else:
                    if isinstance(content, list):
                        for item in content:
                            if item["type"] == "text":
                                st.markdown(item["text"])
                            elif item["type"] == "image_url":
                                img_url = item["image_url"]["url"]
                                uid = f"img_{i}"
                                lb_html = f'''
                                <a href="#{uid}">
                                    <img src="{img_url}" width="150" style="border-radius:10px;">
                                </a>
                                <div id="{uid}" class="lightbox">
                                    <a href="#_" class="close-btn">&times;</a>
                                    <img src="{img_url}">
                                </div>
                                '''
                                st.markdown(lb_html, unsafe_allow_html=True)
                    else:
                        st.markdown(content)
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])

phrases = ["Say hello!", "Say hi!", "Welcome!", "Type here!", "Ready to chat!", "Write something cool!"]
if "placeholder_text" not in st.session_state:
    st.session_state.placeholder_text = random.choice(phrases)

uploaded_file = st.file_uploader("🖼", type=["image"], label_visibility="collapsed")
if uploaded_file:
    st.image(uploaded_file, width=150)

if prompt := st.chat_input(st.session_state.placeholder_text):
    st.session_state.placeholder_text = random.choice(phrases)
    if uploaded_file:
        base64_image = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
        msg_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
    else:
        msg_content = prompt
    st.session_state.all_chats[st.session_state.current_chat].append({"role": "user", "content": msg_content})
    st.rerun()

if messages and messages[-1]["role"] == "user" and st.session_state.edit_index is None:
    with st.chat_message("assistant"):
        try:
            last_msg_content = messages[-1]["content"]
            current_is_image = isinstance(last_msg_content, list)
            model = "meta-llama/llama-4-scout-17b-16e-instruct" if current_is_image else "llama-3.3-70b-versatile"
            
            current_date = datetime.now().strftime("%B %d, %Y")
            api_messages = [{"role": "system", "content": f"You are Phistashka AI. Today is {current_date}."}]
            
            for m in messages:
                m_content = m["content"]
                # If we are using the text model, we MUST convert any list content into a string
                if model == "llama-3.3-70b-versatile" and isinstance(m_content, list):
                    text_part = next((item["text"] for item in m_content if item["type"] == "text"), "")
                    m_content = f"[User sent an image] {text_part}"
                
                api_messages.append({"role": m["role"], "content": m_content})
            
            completion = client.chat.completions.create(model=model, messages=api_messages)
            response_text = completion.choices[0].message.content
            if response_text:
                st.markdown(response_text)
                st.session_state.all_chats[st.session_state.current_chat].append({"role": "assistant", "content": response_text})
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
