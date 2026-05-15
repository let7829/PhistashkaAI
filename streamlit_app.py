import streamlit as st
import google.generativeai as genai

api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

st.title("Phistashka AI")

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {} 
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

with st.sidebar:
    st.header("Chat History")
    
    if st.button("➕ New Chat"):
        new_name = f"Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_name] = []
        st.session_state.current_chat = new_name
        st.rerun()

    st.divider()

    if not st.session_state.all_chats:
        st.write("No chats found.")
    else:
        for chat_name in st.session_state.all_chats.keys():
            if st.button(chat_name):
                st.session_state.current_chat = chat_name
                st.rerun()

if st.session_state.current_chat is None:
    st.info("👈 Open the menu (top left) to start a New Chat!")
else:
    messages = st.session_state.all_chats[st.session_state.current_chat]

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Say hello!"):
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash-lite')
                
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
                    st.error("Empty response. Check safety settings.")
                    
            except Exception as e:
                st.error(f"Error: {e}")
