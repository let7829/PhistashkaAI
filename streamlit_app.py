import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

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
    if message["role"] == "user":
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
                if st.session_state.edit_index == i:
                    edit_val = st.text_input("Edit:", value=message["content"], key=f"input_{i}")
                    if st.button("Save", key=f"save_{i}"):
                        messages[i]["content"] = edit_val
                        st.session_state.all_chats[st.session_state.current_chat] = messages[:i+1]
                        st.session_state.edit_index = None
                        st.rerun()
                else:
                    st.markdown(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])

if prompt := st.chat_input("Say hello!"):
    messages.append({"role": "user", "content": prompt})
    st.rerun()

if messages and messages[-1]["role"] == "user" and st.session_state.edit_index is None:
    with st.chat_message("assistant"):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": m["role"], "content": m["content"]} for m in messages]
            )
            response_text = completion.choices[0].message.content
            st.markdown(response_text)
            messages.append({"role": "assistant", "content": response_text})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
