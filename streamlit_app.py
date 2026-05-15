import streamlit as st
from groq import Groq
import base64
import time
import random

# Initialize Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("Phistashka AI")

# State Management
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# Sidebar Logic
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

# Display Messages
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
                
                # Check if editing
                if st.session_state.edit_index == i:
                    # Extract text if content is formatted for Vision API
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
                    # Display Text and Image if it's a list (Vision format)
                    if isinstance(content, list):
                        for item in content:
                            if item["type"] == "text":
                                st.markdown(item["text"])
                            elif item["type"] == "image_url":
                                st.image(item["image_url"]["url"])
                    else:
                        st.markdown(content)
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])

# 30-Second Random Placeholder Logic
phrases = [
    "Say hello!", "Say hi!", "Hello!", "Welcome!", "Hi!", 
    "Say something!", "Hows your day going!", "Greetings!", 
    "Type here!", "What's on your mind?", "Ask me a question!"
]
current_interval = int(time.time() // 30)
random.seed(current_interval)
placeholder_text = random.choice(phrases)
random.seed() # Reset seed so it doesn't affect other random operations

# Image Uploader (placed directly above chat input)
uploaded_file = st.file_uploader("🖼 Upload Photo (Optional)", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
if uploaded_file:
    st.image(uploaded_file, caption="Preview", width=150)

# Chat Input
if prompt := st.chat_input(placeholder_text):
    
    if uploaded_file:
        # Convert image to base64 for Groq Vision API
        base64_image = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
        msg_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
    else:
        # Standard text format
        msg_content = prompt

    messages.append({"role": "user", "content": msg_content})
    st.rerun()

# AI Response Generation
if messages and messages[-1]["role"] == "user" and st.session_state.edit_index is None:
    with st.chat_message("assistant"):
        try:
            # Check if the last message contains an image to switch to a Vision model
            last_msg_content = messages[-1]["content"]
            contains_image = isinstance(last_msg_content, list)
            
            # Use a vision model if an image is attached, otherwise standard versatile model
            model = "llama-3.2-11b-vision-preview" if contains_image else "llama-3.3-70b-versatile"
            
            api_messages = []
            for m in messages:
                api_messages.append({
                    "role": m["role"],
                    "content": m["content"]
                })
            
            completion = client.chat.completions.create(
                model=model,
                messages=api_messages
            )
            
            response_text = completion.choices[0].message.content
            
            if response_text:
                st.markdown(response_text)
                messages.append({"role": "assistant", "content": response_text})
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
