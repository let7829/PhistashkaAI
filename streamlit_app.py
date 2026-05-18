import streamlit as st

translations = {
    "English": {
        "title": "Phistashka AI",
        "upload": "Upload images",
        "personality": "AI Personality",
        "theme": "Theme Changer",
        "key_prompt": "Enter your API Key:",
        "lang_caption": "🌐 Change language / Поменять язык",
        "chat_placeholder": "Ask Phistashka something...",
        "clear_chat": "Clear Chat",
        "submit": "Submit",
        "personalities": ["Standard", "Aggressive", "Socrates", "Lazy"],
        "themes": ["Dark", "Light", "Pistachio Green"]
    },
    "Русский": {
        "title": "Фисташка ИИ",
        "upload": "Загрузить изображения",
        "personality": "Характер ИИ",
        "theme": "Смена темы",
        "key_prompt": "Введите ваш API ключ:",
        "lang_caption": "🌐 Поменять язык / Change language",
        "chat_placeholder": "Спросите Фисташку о чем-то...",
        "clear_chat": "Очистить чат",
        "submit": "Подтвердить",
        "personalities": ["Обычный", "Агрессивный", "Сократ", "Ленивый"],
        "themes": ["Темная", "Светлая", "Фисташковая"]
    },
    "Українська": {
        "title": "Фісташка ШІ",
        "upload": "Завантажити зображення",
        "personality": "Характер ШІ",
        "theme": "Зміна теми",
        "key_prompt": "Введіть ваш API ключ:",
        "lang_caption": "🌐 Змінити мову / Change language",
        "chat_placeholder": "Запитайте Фісташку про щось...",
        "clear_chat": "Очистити чат",
        "submit": "Підтвердити",
        "personalities": ["Звичайний", "Агресивний", "Сократ", "Лінивий"],
        "themes": ["Темна", "Світла", "Фісташкова"]
    }
}

if 'lang' not in st.session_state:
    st.session_state['lang'] = 'English'
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'Dark' if st.session_state['lang'] == 'English' else 'Темная'
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ""

def change_language():
    st.session_state['lang'] = st.session_state['new_lang']

current_theme = st.session_state['theme']
if current_theme in ["Dark", "Темная"]:
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        [data-testid="stSidebar"] { background-color: #161b22; }
        </style>
    """, unsafe_allowed_html=True)
elif current_theme in ["Light", "Светлая"]:
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; color: #000000; }
        [data-testid="stSidebar"] { background-color: #f0f2f6; }
        </style>
    """, unsafe_allowed_html=True)
elif current_theme in ["Pistachio Green", "Фисташковая"]:
    st.markdown("""
        <style>
        .stApp { background-color: #e2f0d9; color: #1c3b0f; }
        [data-testid="stSidebar"] { background-color: #c5e1a5; }
        div[data-testid="stChatMessage"] { background-color: #d0e1be; }
        </style>
    """, unsafe_allowed_html=True)

lang = st.session_state['lang']
t = translations[lang]

if not st.session_state['api_key']:
    st.title(t["title"])
    st.info(t["lang_caption"])
    lang_list = list(translations.keys())
    st.selectbox(
        "Choose Language / Выберите язык", 
        lang_list, 
        index=lang_list.index(lang), 
        key='new_lang', 
        on_change=change_language
    )
    with st.form("key_form"):
        user_key = st.text_input(t["key_prompt"], type="password")
        submitted = st.form_submit_button(t["submit"])
        if submitted and user_key:
            st.session_state['api_key'] = user_key
            st.rerun()
    st.stop()

st.title(t["title"])

with st.sidebar:
    lang_list = list(translations.keys())
    st.selectbox(
        "Language", 
        lang_list, 
        index=lang_list.index(lang), 
        key='sidebar_lang', 
        on_change=lambda: st.session_state.update({'lang': st.session_state['sidebar_lang']})
    )
    st.write("---")
    st.write(f"### {t['theme']}")
    chosen_theme = st.radio(
        "", 
        t["themes"], 
        index=t["themes"].index(current_theme) if current_theme in t["themes"] else 0
    )
    if chosen_theme != current_theme:
        st.session_state['theme'] = chosen_theme
        st.rerun()
    st.write("---")
    st.write(f"### {t['personality']}")
    st.selectbox("", t["personalities"])
    st.write("---")
    st.file_uploader(t["upload"], type=["png", "jpg", "jpeg"])
    if st.button(t["clear_chat"]):
        st.session_state['messages'] = []
        st.rerun()

for msg in st.session_state['messages']:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input(t["chat_placeholder"]):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        response = f" [Phistashka processed: {prompt}]"
        st.write(response)
    st.session_state['messages'].append({"role": "assistant", "content": response})
