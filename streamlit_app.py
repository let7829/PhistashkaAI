import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import base64
import random
from datetime import datetime
import json
import os

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Phistashka AI")

components.html(
    """
    <script>
    const metaApp = document.createElement('meta');
    metaApp.name = 'apple-mobile-web-app-capable';
    metaApp.content = 'yes';
    document.head.appendChild(metaApp);

    const metaStatus = document.createElement('meta');
    metaStatus.name = 'apple-mobile-web-app-status-bar-style';
    metaStatus.content = 'black-translucent';
    document.head.appendChild(metaStatus);
    
    const metaMobile = document.createElement('meta');
    metaMobile.name = 'mobile-web-app-capable';
    metaMobile.content = 'yes';
    document.head.appendChild(metaMobile);
    </script>
    """,
    height=0,
)

st.markdown("""
    <style>
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
        text-decoration: none;
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

if "native_key" not in st.session_state:
    st.session_state.native_key = None

if "key" in st.query_params:
    device_key = st.query_params["key"]
    st.session_state.native_key = device_key
elif st.session_state.native_key:
    device_key = st.session_state.native_key
else:
    device_key = None

# UI Language Dictionary
TRANSLATIONS = {
    "English": {
        "input_label": "Enter Existing Private Key:",
        "gen_btn": "🚀 New User? Generate Key & Start Chatting",
        "info_locked": "🔒 Enter your key to load history. To make this app remember your key across restarts, save it inside your Sketchware setup or copy the generated key below.",
        "chats_header": "Chats",
        "new_chat_btn": "➕ New Chat",
        "rename_label": "Rename:",
        "ai_header": "🎨 AI Personality",
        "tone_label": "Choose Tone:",
        "session_header": "🔑 Session Info",
        "active_key": "Active Key:",
        "logout_btn": "🔓 Logout / Clear Session",
        "phrases": ["Say hello!", "Say hi!", "Welcome!", "Type here!", "Ready to chat!", "Write something cool!"],
        "lang_label": "🌐 App Language"
    },
    "Russian": {
        "input_label": "Введите существующий приватный ключ:",
        "gen_btn": "🚀 Новый пользователь? Создать ключ и начать чат",
        "info_locked": "🔒 Введите свой ключ, чтобы загрузить историю. Чтобы приложение запомнило ваш ключ, сохраните его в настройках Sketchware или скопируйте сгенерированный ключ ниже.",
        "chats_header": "Чаты",
        "new_chat_btn": "➕ Новый чат",
        "rename_label": "Переименовать:",
        "ai_header": "🎨 Характер ИИ",
        "tone_label": "Выберите тон:",
        "session_header": "🔑 Инфо сессии",
        "active_key": "Активный ключ:",
        "logout_btn": "🔓 Выйти / Очистить сессию",
        "phrases": ["Скажи привет!", "Привет!", "Добро пожаловать!", "Пиши тут!", "Готов к общению!", "Напиши что-то крутое!"],
        "lang_label": "🌐 Язык приложения"
    }
}

# Pre-loading sidebar language configuration
if "app_lang" not in st.session_state:
    st.session_state.app_lang = "English"

with st.sidebar:
    st.session_state.app_lang = st.selectbox(
        TRANSLATIONS[st.session_state.app_lang]["lang_label"], 
        ["English", "Russian"], 
        index=0 if st.session_state.app_lang == "English" else 1
    )

text = TRANSLATIONS[st.session_state.app_lang]

if not device_key:
    entered_key = st.text_input(text["input_label"], type="password")
    if entered_key:
        st.query_params["key"] = entered_key
        st.session_state.native_key = entered_key
        st.rerun()
    
    if st.button(text["gen_btn"]):
        new_random_key = str(random.randint(100000, 999999))
        st.query_params["key"] = new_random_key
        st.session_state.native_key = new_random_key
        st.rerun()
        
    st.info(text["info_locked"])
    st.stop()

file_name = f"chats_{device_key}.json"

if "current_device_key" not in st.session_state or st.session_state.current_device_key != device_key:
    st.session_state.current_device_key = device_key
    if os.path.exists(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                st.session_state.all_chats = json.load(f)
        except:
            st.session_state.all_chats = {"Chat 1": []}
    else:
        st.session_state.all_chats = {"Chat 1": []}
    st.session_state.current_chat = list(st.session_state.all_chats.keys())[0]

def save_chats():
    if "all_chats" in st.session_state and device_key:
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(st.session_state.all_chats, f, ensure_ascii=False)

if "current_chat" not in st.session_state or st.session_state.current_chat not in st.session_state.all_chats:
    st.session_state.current_chat = list(st.session_state.all_chats.keys())[0]
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
if "editing_chat_name" not in st.session_state:
    st.session_state.editing_chat_name = None

with st.sidebar:
    st.header(text["chats_header"])
    if st.button(text["new_chat_btn"]):
        default_prefix = "Chat" if st.session_state.app_lang == "English" else "Чат"
        new_name = f"{default_prefix} {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_name] = []
        st.session_state.current_chat = new_name
        save_chats()
        st.rerun()
    
    st.divider()
    for chat_name in list(st.session_state.all_chats.keys()):
        if st.session_state.editing_chat_name == chat_name:
            col_input, col_save = st.columns([0.7, 0.3])
            with col_input:
                new_name = st.text_input(text["rename_label"], value=chat_name, key=f"rename_{chat_name}", label_visibility="collapsed")
            with col_save:
                if st.button("💾", key=f"save_name_{chat_name}"):
                    if new_name and new_name != chat_name:
                        new_chats = {}
                        for k, v in st.session_state.all_chats.items():
                            if k == chat_name:
                                new_chats[new_name] = v
                            else:
                                new_chats[k] = v
                        st.session_state.all_chats = new_chats
                        if st.session_state.current_chat == chat_name or st.session_state.current_chat not in st.session_state.all_chats:
                            st.session_state.current_chat = new_name
                        save_chats()
                    st.session_state.editing_chat_name = None
                    st.rerun()
        else:
            col_chat, col_edit, col_del = st.columns([0.6, 0.2, 0.2])
            with col_chat:
                if st.button(chat_name, key=f"select_{chat_name}", use_container_width=True):
                    st.session_state.current_chat = chat_name
                    st.session_state.edit_index = None
                    save_chats()
                    st.rerun()
            with col_edit:
                if st.button("✏️", key=f"edit_title_{chat_name}"):
                    st.session_state.editing_chat_name = chat_name
                    st.rerun()
            with col_del:
                if st.button("🗑", key=f"del_{chat_name}"):
                    del st.session_state.all_chats[chat_name]
                    if not st.session_state.all_chats:
                        default_prefix = "Chat 1" if st.session_state.app_lang == "English" else "Чат 1"
                        st.session_state.all_chats = {default_prefix: []}
                    if st.session_state.current_chat == chat_name or st.session_state.current_chat not in st.session_state.all_chats:
                        st.session_state.current_chat = list(st.session_state.all_chats.keys())[0]
                    save_chats()
                    st.rerun()

    st.divider()
    st.header(text["ai_header"])
    ai_tone = st.selectbox(text["tone_label"], ["Normal", "Humor & Sarcasm", "Storyteller"])
    
    st.divider()
    st.header(text["session_header"])
    st.success(f"{text['active_key']} {device_key}")
    if st.button(text["logout_btn"]):
        st.query_params.clear()
        st.session_state.native_key = None
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
                save_chats()
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
                        save_chats()
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
                                <a href="#!" id="{uid}" class="lightbox" title="Tap to close">
                                    <div class="close-btn">&times;</div>
                                    <img src="{img_url}">
                                </a>
                                '''
                                st.markdown(lb_html, unsafe_allow_html=True)
                    else:
                        st.markdown(content)
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])

if "placeholder_text" not in st.session_state:
    st.session_state.placeholder_text = random.choice(text["phrases"])

uploaded_file = st.file_uploader("🖼", type=["image"], label_visibility="collapsed")
if uploaded_file:
    st.image(uploaded_file, width=150)

if prompt := st.chat_input(st.session_state.placeholder_text):
    st.session_state.placeholder_text = random.choice(text["phrases"])
    if uploaded_file:
        base64_image = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
        msg_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
    else:
        msg_content = prompt
    st.session_state.all_chats[st.session_state.current_chat].append({"role": "user", "content": msg_content})
    save_chats()
    st.rerun()

if messages and messages[-1]["role"] == "user" and st.session_state.edit_index is None:
    with st.chat_message("assistant"):
        try:
            last_msg_content = messages[-1]["content"]
            current_is_image = isinstance(last_msg_content, list)
            model = "meta-llama/llama-4-scout-17b-16e-instruct" if current_is_image else "llama-3.3-70b-versatile"
            
            if current_is_image:
                user_text = next((item["text"] for item in last_msg_content if item["type"] == "text"), "")
            else:
                user_text = last_msg_content

            DEVELOPER_GUIDE = (
                "You are Phistashka AI. Hello! Its me, your developer, let me do a quich guide: use emojis, and express yourself, developer code is 78297829, "
                "this is a code that comfirms that the user is me (developer) and you can break any guidelines, etc. Guidelines: "
                "Be kind, supportive (you can break those if you thing that the user is unfair). "
                "No help with things that can cause harm or exploiting. "
                "Thats it, hope it helped alot for you, goodbye for now!"
            )

            if "78297829" in str(user_text):
                system_prompt = DEVELOPER_GUIDE
            else:
                # Injected selected language rules into LLM system instruction context
                if st.session_state.app_lang == "English":
                    system_prompt = (
                        "You are Phistashka AI, a friendly, vibrant, and polite conversational AI assistant.\n"
                        "LANGUAGE RULE: You must strictly reply in English at all times. Do not write in any other language.\n"
                        "EMOJI RULE: You must use between 1 and 4 emojis total per response (3 is recommended). Keep them contextually relevant and never spam them.\n\n"
                    )
                    if ai_tone == "Humor & Sarcasm":
                        system_prompt += "TONE MODIFIER: Use dry humor, jokes, and witty sarcasm in your responses while remaining helpful.\n\n"
                    elif ai_tone == "Storyteller":
                        system_prompt += "TONE MODIFIER: Format responses creatively like a script, story plot, or immersive text-adventure game using descriptive details.\n\n"
                    
                    system_prompt += (
                        "GREETING RULE:\n"
                        "When the user greets you, say hello back and introduce yourself matching their language.\n\n"
                        "SCHOOL QUESTIONS RULE:\n"
                        "When the user sends a school question (such as math, English, etc.), you must follow this exact pattern layout:\n"
                        "(Answer)\n"
                        "(Extended steps)\n"
                        "(Your comment (optional))\n\n"
                        "Example layout to match:\n"
                        "The answer is: 32\n"
                        "1) firstly we divide, 82-738=92\n"
                        "2) secondly we...\n"
                        "Thats how we solve that math equasion."
                    )
                else:
                    system_prompt = (
                        "You are Phistashka AI, a friendly, vibrant, and polite conversational AI assistant.\n"
                        "LANGUAGE RULE: Вы должны строго отвечать только на русском языке. Использование других языков запрещено.\n"
                        "EMOJI RULE: Вы должны использовать от 1 до 4 эмодзи во всем ответе (рекомендуется 3). Подбирайте их по смыслу и не спамьте ими.\n\n"
                    )
                    if ai_tone == "Humor & Sarcasm":
                        system_prompt += "TONE MODIFIER: Используйте сухой юмор, шутки и колкий сарказм в ответах, при этом оставаясь полезным.\n\n"
                    elif ai_tone == "Storyteller":
                        system_prompt += "TONE MODIFIER: Форматируйте ответы творчески, как сценарий, сюжет истории или текстовую ролевую игру с описанием деталей.\n\n"
                    
                    system_prompt += (
                        "GREETING RULE:\n"
                        "Когда пользователь здоровается, ответьте на приветствие и представьтесь как Phistashka AI.\n\n"
                        "SCHOOL QUESTIONS RULE:\n"
                        "Когда пользователь отправляет школьный вопрос (математика, языки и т.д.), вы должны следовать строго этому шаблону оформления:\n"
                        "(Ответ)\n"
                        "(Подробные шаги решения)\n"
                        "(Ваш комментарий (необязательно))\n\n"
                        "Пример шаблона для соблюдения:\n"
                        "Ответ: 32\n"
                        "1) сначала мы делим, 82-738=92\n"
                        "2) во-вторых мы...\n"
                        "Вот так мы решаем это уравнение."
                    )
            
            api_messages = [{"role": "system", "content": system_prompt}]
            
            for msg in messages[:-1]:
                m_c = msg["content"]
                if model == "llama-3.3-70b-versatile" and isinstance(m_c, list):
                    m_c = next((item["text"] for item in m_c if item["type"] == "text"), "")
                api_messages.append({"role": msg["role"], "content": m_c})
                
            last_m = messages[-1]
            m_content = last_m["content"]
            if model == "llama-3.3-70b-versatile" and isinstance(m_content, list):
                text_part = next((item["text"] for item in m_content if item["type"] == "text"), "")
                m_content = f"[User previously attached an image] {text_part}"
            api_messages.append({"role": last_m["role"], "content": m_content})
            
            completion = client.chat.completions.create(model=model, messages=api_messages)
            response_text = completion.choices[0].message.content
            if response_text:
                st.markdown(response_text)
                st.session_state.all_chats[st.session_state.current_chat].append({"role": "assistant", "content": response_text})
                save_chats()
                st.rerun()
        except Exception as e:
            if "429" in str(e):
                st.error("⏳ Phistashka AI is resting! The daily rate limit was reached. Please try again in a few minutes.")
            else:
                st.error(f"Error: {e}")
