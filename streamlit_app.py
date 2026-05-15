import streamlit as st
import google.generativeai as genai

api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

st.title("Phistashka AI")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        col1, col2, col3 = st.columns([0.07, 0.07, 0.86])
        
        if col1.button("📝", key=f"edit_{i}"):
            st.session_state.edit_index = i
            st.rerun()
            
        if col2.button("↩️", key=f"undo_{i}"):
            st.session_state.messages = st.session_state.messages[:i]
            st.rerun()
            
        with col3:
            with st.chat_message("user"):
                if st.session_state.edit_index == i:
                    edit_input = st.text_input("Edit your message:", value=message["content"], key=f"input_{i}")
                    if st.button("Save", key=f"save_{i}"):
                        st.session_state.messages[i]["content"] = edit_input
                        st.session_state.messages = st.session_state.messages[:i+1]
                        st.session_state.edit_index = None
                        st.rerun()
                else:
                    st.markdown(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])

if prompt := st.chat_input("Say hello!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and st.session_state.edit_index is None:
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            history = []
            for m in st.session_state.messages[:-1]:
                role = "model" if m["role"] == "assistant" else "user"
                history.append({"role": role, "parts": [m["content"]]})
            
            chat = model.start_chat(history=history)
            response = chat.send_message(st.session_state.messages[-1]["content"])
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
