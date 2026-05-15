import streamlit as st
import google.generativeai as genai

api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

st.title("Phistashka AI")

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

with st.sidebar:
    st.header("Chat Management")
    
    if st.button("➕ New Chat"):
        new_name = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_name] = []
        st.session_state.current_chat = new_name
        st.rerun()

    st.divider()

    if st.session_state.all_chats:
        chat_list = list(st.session_state.all_chats.keys())
        choice = st.selectbox("Select Chat", chat_list, index=chat_list.index(st.session_state.current_chat))
        st.session_state.current_chat = choice

    st.divider()

    if st.button("↩️ Undo Last Message"):
        if st.session_state.all_chats[st.session_state.current_chat]:
            st.session_state.all_chats[st.session_state.current_chat].pop()
            if st.session_state.all_chats[st.session_state.current_chat]:
                st.session_state.all_chats[st.session_state.current_chat].pop()
            st.rerun()

    st.divider()
    st.subheader("Edit Messages")
    msg_index = st.number_input("Message Index", min_value=0, max_value=max(0, len(st.session_state.all_chats[st.session_state.current_chat])-1), step=1)
    new_text = st.text_area("Edit Text")
    if st.button("Update Message"):
        if st.session_state.all_chats[st.session_state.current_chat]:
            st.session_state.all_chats[st.session_state.current_chat][msg_index]["content"] = new_text
            st.rerun()

messages = st.session_state.all_chats[st.session_state.current_chat]

for i, message in enumerate(messages):
    with st.chat_message(message["role"]):
        st.markdown(f"{message['content']} *(Index: {i})*")

if prompt := st.chat_input("Say hello!"):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            formatted_history = []
            for m in messages[:-1]:
                role = "model" if m["role"] == "assistant" else "user"
                formatted_history.append({"role": role, "parts": [m["content"]]})
            
            chat_session = model.start_chat(history=formatted_history)
            response = chat_session.send_message(prompt)
            
            if response.text:
                st.markdown(response.text)
                messages.append({"role": "assistant", "content": response.text})
            else:
                st.error("Empty response.")
                
        except Exception as e:
            st.error(f"Error: {e}")
