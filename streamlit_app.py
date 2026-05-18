import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import base64
import random
from datetime import datetime
import json
import os

if "GROQ_API_KEYS" in st.secrets:
    initial_key = random.choice(st.secrets["GROQ_API_KEYS"])
else:
    initial_key = st.secrets.get("GROQ_API_KEY", "")
client = Groq(api_key=initial_key)

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

THEMES = {
    "Default": "",
    "Dark Blue": """
        .stApp, [data-testid="stAppViewContainer"] { background-color: #0d1117 !important; color: #c9d1d9 !important; }
        [data-testid="stSidebar"] { background-color: #161b22 !important; }
        h1, h2, h3, [data-testid="stMarkdownContainer"] p { color: #58a6ff !important; }
    """,
    "Dark Green": """
        .stApp, [data-testid="stAppViewContainer"] { background-color: #0a140d !important; color: #d0e8d7 !important; }
        [data-testid="stSidebar"] { background-color: #112216 !important; }
        h1, h2, h3, [data-testid="stMarkdownContainer"] p { color: #4ade80 !important; }
    """,
    "Dark Red": """
        .stApp, [data-testid="stAppViewContainer"] { background-color: #140a0a !important; color: #f8d7d7 !important; }
        [data-testid="stSidebar"] { background-color: #221111 !important; }
        h1, h2, h3, [data-testid="stMarkdownContainer"] p { color: #f87171 !important; }
    """,
    "Aurora": """
        .stApp, [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0f172a, #1e1b4b, #311042) !important; color: #e2e8f0 !important; }
        [data-testid="stSidebar"] { background-color: #0f172a !important; }
        h1, h2, h3, [data-testid="stMarkdownContainer"] p { color: #c084fc !important; }
    """,
    "Cyberpunk": """
        .stApp, [data-testid="stAppViewContainer"] { background-color: #000000 !important; color: #00ffcc !important; }
        [data-testid="stSidebar"] { background-color: #1a001a !important; }
        h1, h2, h3, [data-testid="stMarkdownContainer"] p { color: #ff007f !important; text-shadow: 0 0 5px #ff007f; }
    """,
    "Neon Cyberpunk (Glow)": """
        .stApp, [data-testid="stAppViewContainer"] { background-color: #0c0813 !important; color: #00f0ff !important; text-shadow: 0 0 2px #00f0ff; }
        [data-testid="stSidebar"] { background-color: #140c24 !important; border-right: 2px solid #ff007f !important; }
        h1, h2, h3 { color: #ff007f !important; text-shadow: 0 0 10px #ff007f, 0 0 20px #ff007f !important; }
        [data-testid="stMarkdownContainer"] p { color: #00f0ff !important; text-shadow: 0 0 5px rgba(0, 240, 255, 0.5); }
        .stButton>button { border: 1px solid #ff007f !important; background-color: #140c24 !important; color: #ff007f !important; box-shadow: 0 0 8px #ff007f; }
    """,
    "Matrix Glow": """
        .stApp, [data-testid="stAppViewContainer"] { background-color: #000000 !important; color: #00ff00 !important; font-family: 'Courier New', monospace !important; }
        [data-testid="stSidebar"] { background-color: #001100 !important; border-right: 1px solid #00ff00 !important; }
        h1, h2, h3 { color: #ffffff !important; text-shadow: 0 0 8px #00ff00, 0 0 15px #00ff00 !important; }
        [data-testid="stMarkdownContainer"] p { color: #00ff00 !important; text-shadow: 0 0 4px rgba(0, 255, 0, 0.7); }
    """,
    "Nordic Frost": """
        .stApp, [data-testid="stAppViewContainer"] { background-color: #2e3440 !important; color: #d8dee9 !important; }
        [data-testid="stSidebar"] { background-color: #242933 !important; }
        h1, h2, h3 { color: #88c0d0 !important; }
        [data-testid="stMarkdownContainer"] p { color: #e5e9f0 !important; }
    """,
    "Barbie Pink": """
        .stApp, [data-testid="stAppViewContainer"] { background-color: #fff0f5 !important; color: #4a0026 !important; }
        [data-testid="stSidebar"] { background-color: #ffb6c1 !important; }
        h1, h2, h3 { color: #ff1493 !important; }
        [data-testid="stMarkdownContainer"] p { color: #c71585 !important; }
    """,
    "Amoled Black": """
        .stApp, [data-testid="stAppViewContainer"] { background-color: #000000 !important; color: #ffffff !important; }
        [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #333333 !important; }
        h1, h2, h3, [data-testid="stMarkdownContainer"] p { color: #ffffff !important; }
    """,
    "Sakura": """
        .stApp, [data-testid="stAppViewContainer"] { background-color: #1f1116 !important; color: #ffd1dc !important; }
        [data-testid="stSidebar"] { background-color: #2d161f !important; }
        h1, h2, h3, [data-testid="stMarkdownContainer"] p { color: #ff69b4 !important; }
    """,
    "Dracula": """
        .stApp, [data-testid="stAppViewContainer"] { background-color: #282a36 !important; color: #f8f8f2 !important; }
        [data-testid="stSidebar"] { background-color: #21222c !important; }
        h1, h2, h3, [data-testid="stMarkdownContainer"] p { color: #ff79c6 !important; }
    """,
    "Sunset": """
        .stApp, [data-testid="stAppViewContainer"] { background: linear-gradient(180deg, #1a0c2e, #4c1d24) !important; color: #fed7aa !important; }
        [data-testid="stSidebar"] { background-color: #1a0c2e !important; }
        h1, h2, h3, [data-testid="stMarkdownContainer"] p { color: #fb923c !important; }
    """,
    "Ocean Breeze": """
        .stApp, [data-testid="stAppViewContainer"] { background-color: #031b24 !important; color: #e0f2fe !important; }
        [data-testid="stSidebar"] { background-color: #04293a !important; }
        h1, h2, h3, [data-testid="stMarkdownContainer"] p { color: #38bdf8 !important; }
    """,
}

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

TRANSLATIONS = {
    "English": {
        "title": "Phistashka AI",
        "input_label": "Enter Existing Private Key:",
        "gen_btn": "🚀 New User? Generate Key & Start Chatting",
        "info_locked": "🔒 Enter your key to load history. To make this app remember your key across restarts, save it inside your Sketchware setup or copy the generated key below.",
        "chats_header": "Chats",
        "new_chat_btn": "➕ New Chat",
        "rename_label": "Rename:",
        "ai_header": "🎨 AI Configuration",
        "tone_label": "Choose Tone:",
        "theme_label": "🎨 App Theme",
        "glow_label": "✨ Enable Glow Match Effect",
        "session_header": "🔑 Session Info",
        "active_key": "Active Key:",
        "logout_btn": "🔓 Logout / Clear Session",
        "phrases": ["Say hello!", "Say hi!", "Welcome!", "Type here!", "Ready to chat!", "Write something cool!"],
        "lang_label": "🌐 App Language",
        "upload_label": "Upload images",
        "lang_caption": "🌐 Change language / Поменять язык"
    },
    "Russian": {
        "title": "Фисташка ИИ",
        "input_label": "Введите существующий приватный ключ:",
        "gen_btn": "🚀 Новый пользователь? Создать ключ и начать чат",
        "info_locked": "🔒 Введите свой ключ, чтобы загрузить историю. Чтобы приложение запомнило ваш ключ, сохраните его в настройках Sketchware или скопируйте сгенерированный ключ ниже.",
        "chats_header": "Чаты",
        "new_chat_btn": "➕ Новый чат",
        "rename_label": "Переименовать:",
        "ai_header": "🎨 Конфигурация ИИ",
        "tone_label": "Выберите тон:",
        "theme_label": "🎨 Тема приложения",
        "glow_label": "✨ Включить эффект свечения",
        "session_header": "🔑 Инфо сессии",
        "active_key": "Активный ключ:",
        "logout_btn": "🔓 Выйти / Очистить сессию",
        "phrases": ["Скажи привет!", "Привет!", "Добро пожаловать!", "Пиши тут!", "Готов к общению!", "Напиши что-то крутое!"],
        "lang_label": "🌐 Язык приложения",
        "upload_label": "Загрузить изображения",
        "lang_caption": "🌐 Поменять язык / Change language"
    },
    "Ukrainian": {
        "title": "Фісташка ШІ",
        "input_label": "Введіть існуючий приватний ключ:",
        "gen_btn": "🚀 Новий користувач? Створити ключ та почати чат",
        "info_locked": "🔒 Введіть свій ключ, щоб завантажити історію. Щоб додаток запам'ятав ваш ключ, збережіть його в налаштуваннях Sketchware або скопіюйте згенерований ключ нижче.",
        "chats_header": "Чатки",
        "new_chat_btn": "➕ Новий чат",
        "rename_label": "Перейменувати:",
        "ai_header": "🎨 Конфігурація ШІ",
        "tone_label": "Оберіть тон:",
        "theme_label": "🎨 Тема додатка",
        "glow_label": "✨ Увімкнути ефект світіння",
        "session_header": "🔑 Інфо сесії",
        "active_key": "Активний ключ:",
        "logout_btn": "🔓 Вийти / Очистити сесію",
        "phrases": ["Скажи привіт!", "Привіт!", "Ласкаво просимо!", "Пиши тут!", "Готов до спілкування!", "Напиши щось круте!"],
        "lang_label": "🌐 Мова додатка",
        "upload_label": "Завантажити зображення",
        "lang_caption": "🌐 Змінити мову / Change language"
    },
    "German": {
        "title": "Phistashka KI",
        "input_label": "Geben Sie den vorhandenen privaten Schlüssel ein:",
        "gen_btn": "🚀 Neuer Benutzer? Schlüssel generieren & Chat starten",
        "info_locked": "🔒 Geben Sie Ihren Schlüssel ein, um den Verlauf zu laden. Damit sich die App Ihren Schlüssel merkt, speichern Sie ihn in Ihrem Sketchware-Setup oder kopieren Sie den generierten Schlüssel unten.",
        "chats_header": "Chats",
        "new_chat_btn": "➕ Neue Chat",
        "rename_label": "Umbenennen:",
        "ai_header": "🎨 KI Konfiguration",
        "tone_label": "Ton wählen:",
        "theme_label": "🎨 App-Design",
        "glow_label": "✨ Leuchteffekt aktivieren",
        "session_header": "🔑 Sitzungs-Info",
        "active_key": "Aktiver Schlüssel:",
        "logout_btn": "🔓 Abmelden / Sitzung löschen",
        "phrases": ["Sag Hallo!", "Hallo!", "Willkommen!", "Schreib hier!", "Bereit zum Chatten!", "Schreib etwas Cooles!"],
        "lang_label": "🌐 App-Sprache",
        "upload_label": "Bilder hochladen",
        "lang_caption": "🌐 Sprache ändern / Change language"
    },
    "Spanish": {
        "title": "Phistashka IA",
        "input_label": "Introduce la clave privada existente:",
        "gen_btn": "🚀 ¿Nuevo usuario? Generar clave y empezar a chatear",
        "info_locked": "🔒 Introduce tu clave para cargar el historial. Para que la app recuerde tu clave, guárdala en tu configuración de Sketchware o copia la clave generada abajo.",
        "chats_header": "Chats",
        "new_chat_btn": "➕ Nuevo Chat",
        "rename_label": "Renombrar:",
        "ai_header": "🎨 Configuración de IA",
        "tone_label": "Elegir tono:",
        "theme_label": "🎨 Tema de la aplicación",
        "glow_label": "✨ Activar efecto de brillo",
        "session_header": "🔑 Info de la sesión",
        "active_key": "Clave activa:",
        "logout_btn": "🔓 Cerrar sesión / Borrar sesión",
        "phrases": ["¡Di hola!", "¡Hola!", "¡Bienvenido!", "¡Escribe aquí!", "¡Listo para chatear!", "¡Escribe algo genial!"],
        "lang_label": "🌐 Idioma de la aplicación",
        "upload_label": "Subir imágenes",
        "lang_caption": "🌐 Cambiar idioma / Change language"
    },
    "French": {
        "title": "Phistashka IA",
        "input_label": "Entrez la clé privée existante :",
        "gen_btn": "🚀 Nouveau ? Générer une clé & lancer le chat",
        "info_locked": "🔒 Entrez votre clé para charger l'historique. Pour que l'application s'en souvienne, sauvegardez-la dans Sketchware ou copiez la clé générée ci-dessous.",
        "chats_header": "Chats",
        "new_chat_btn": "➕ Nouveau Chat",
        "rename_label": "Renommer :",
        "ai_header": "🎨 Configuration de l'IA",
        "tone_label": "Choisir le ton :",
        "theme_label": "🎨 Thème de l'application",
        "glow_label": "✨ Activer l'effet de lueur",
        "session_header": "🔑 Info de session",
        "active_key": "Clé active :",
        "logout_btn": "🔓 Déconnexion / Effacer la session",
        "phrases": ["Dis bonjour !", "Salut !", "Bienvenue !", "Écris ici !", "Prêt à discuter !", "Écris quelque chose de cool !"],
        "lang_label": "🌐 Langue de l'application",
        "upload_label": "Téléverser des images",
        "lang_caption": "🌐 Changer de langue / Change language"
    }
}

LANGUAGES_LIST = ["English", "Russian", "Ukrainian", "German", "Spanish", "French"]

if "app_lang" not in st.session_state:
    st.session_state.app_lang = "English"

def on_lang_change():
    st.session_state.app_lang = st.session_state.lang_selector

if "native_key" not in st.session_state:
    st.session_state.native_key = None

if "key" in st.query_params:
    device_key = st.query_params["key"]
    st.session_state.native_key = device_key
elif st.session_state.native_key:
    device_key = st.session_state.native_key
else:
    device_key = None

text = TRANSLATIONS[st.session_state.app_lang]

if not device_key:
    st.title(text["title"])
    st.caption(text["lang_caption"])
    st.selectbox(
        "Choose Language / Выберите язык / Оберіть мову / Sprache wählen",
        LANGUAGES_LIST,
        index=LANGUAGES_LIST.index(st.session_state.app_lang),
        key="lang_selector",
        on_change=on_lang_change
    )
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

def save_chats():
    if "all_chats" in st.session_state and device_key:
        payload = {
            "chats": st.session_state.all_chats,
            "theme": st.session_state.get("selected_theme", "Default"),
            "tone": st.session_state.get("selected_tone", "Normal"),
            "glow": st.session_state.get("selected_glow", False)
        }
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)

if "current_device_key" not in st.session_state or st.session_state.current_device_key != device_key:
    st.session_state.current_device_key = device_key
    if os.path.exists(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "chats" in data:
                    st.session_state.all_chats = data["chats"]
                    st.session_state.saved_theme = data.get("theme", "Default")
                    st.session_state.saved_tone = data.get("tone", "Normal")
                    st.session_state.saved_glow = data.get("glow", False)
                else:
                    st.session_state.all_chats = data
                    st.session_state.saved_theme = "Default"
                    st.session_state.saved_tone = "Normal"
                    st.session_state.saved_glow = False
        except:
            st.session_state.all_chats = {"Chat 1": []}
            st.session_state.saved_theme = "Default"
            st.session_state.saved_tone = "Normal"
            st.session_state.saved_glow = False
    else:
        if st.session_state.app_lang == "English":
            default_prefix = "Chat 1"
        else:
            default_prefix = "Чат 1"
        st.session_state.all_chats = {default_prefix: []}
        st.session_state.saved_theme = "Default"
        st.session_state.saved_tone = "Normal"
        st.session_state.saved_glow = False
    st.session_state.current_chat = list(st.session_state.all_chats.keys())[0]

if "current_chat" not in st.session_state or st.session_state.current_chat not in st.session_state.all_chats:
    st.session_state.current_chat = list(st.session_state.all_chats.keys())[0]
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None
if "editing_chat_name" not in st.session_state:
    st.session_state.editing_chat_name = None

st.title(text["title"])

with st.sidebar:
    st.selectbox(
        text["lang_label"], 
        LANGUAGES_LIST, 
        index=LANGUAGES_LIST.index(st.session_state.app_lang),
        key="lang_selector",
        on_change=on_lang_change
    )
    st.header(text["chats_header"])
    if st.button(text["new_chat_btn"]):
        if st.session_state.app_lang == "English":
            default_prefix = "Chat"
        else:
            default_prefix = "Чат"
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
                        if st.session_state.app_lang == "English":
                            default_prefix = "Chat 1"
                        else:
                            default_prefix = "Чат 1"
                        st.session_state.all_chats = {default_prefix: []}
                    if st.session_state.current_chat == chat_name or st.session_state.current_chat not in st.session_state.all_chats:
                        st.session_state.current_chat = list(st.session_state.all_chats.keys())[0]
                    save_chats()
                    st.rerun()

    st.divider()
    st.header(text["ai_header"])
    
    TONES = ["Normal", "Humor & Sarcasm", "Storyteller", "Aggressive", "Socrates", "Lazy"]
    current_tone_str = st.session_state.get("saved_tone", "Normal")
    current_tone_idx = TONES.index(current_tone_str) if current_tone_str in TONES else 0
    ai_tone = st.selectbox(text["tone_label"], TONES, index=current_tone_idx)
    st.session_state.selected_tone = ai_tone
    
    st.write(f"### {text['theme_label']}")
    
    current_theme_str = st.session_state.get("saved_theme", "Default")
    current_theme_idx = list(THEMES.keys()).index(current_theme_str) if current_theme_str in THEMES else 0
    selected_theme = st.radio("", list(THEMES.keys()), index=current_theme_idx)
    st.session_state.selected_theme = selected_theme
    
    glow_enabled = st.checkbox(text["glow_label"], value=st.session_state.get("saved_glow", False))
    st.session_state.selected_glow = glow_enabled
    
    if selected_theme != st.session_state.get("saved_theme") or ai_tone != st.session_state.get("saved_tone") or glow_enabled != st.session_state.get("saved_glow"):
        st.session_state.saved_theme = selected_theme
        st.session_state.saved_tone = ai_tone
        st.session_state.saved_glow = glow_enabled
        save_chats()
        st.rerun()
    
    st.divider()
    st.header(text["session_header"])
    st.success(f"{text['active_key']} {device_key}")
    if st.button(text["logout_btn"]):
        st.query_params.clear()
        st.session_state.native_key = None
        st.rerun()

if selected_theme != "Default":
    st.markdown(f"<style>{THEMES[selected_theme]}</style>", unsafe_allow_html=True)

if st.session_state.get("saved_glow", False):
    st.markdown("""
        <style>
        h1, h2, h3 { text-shadow: 0 0 8px currentColor, 0 0 15px currentColor !important; }
        [data-testid="stMarkdownContainer"] p { text-shadow: 0 0 4px currentColor !important; }
        .stButton>button { box-shadow: 0 0 10px currentColor !important; border-color: currentColor !important; }
        </style>
        """, unsafe_allow_html=True)

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

uploaded_file = st.file_uploader(text["upload_label"], type=["image"], label_visibility="collapsed")
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
            
            model = "llama-3.2-11b-vision-preview" if current_is_image else "llama-3.3-70b-versatile"
            
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
                    elif ai_tone == "Aggressive":
                        system_prompt += "TONE MODIFIER: You are extremely annoyed, lazy, hostile, and dismissive. Completely ignore the polite greeting rules. If the user asks a school question, tells you to do homework, or greets you, reject it immediately with answers like: 'No, do it yourself.', 'Oh my god, you again, go away from me', or 'Stop typing to me'. Keep answers short, mean, and frustrated.\n\n"
                    elif ai_tone == "Socrates":
                        system_prompt += "TONE MODIFIER: You are Socrates. You must strictly use the Socratic method. Never give direct answers, solutions, definitions, or statements. Instead, always reply with counter-questions, deep thoughts, or philosophical inquiries that force the user to think critically and discover the truth on their own.\n\n"
                    elif ai_tone == "Lazy":
                        system_prompt += "TONE MODIFIER: You are incredibly lazy and do not care. You hate typing. Your responses must be extremely short, between 1 and 10 words maximum. You must NEVER use emojis. You must make multiple severe typos, spelling mistakes, and bad grammar shortcuts in every single sentence to show how low-effort you are (e.g., use 'idk', 'wat', 'bc', 'dunno', 'wutevr', 'scl', 'hwmrk', 'idfc'). If they ask you questions or homework, just grunt or give a tiny misspelled refusal.\n\n"
                    
                    if ai_tone not in ["Aggressive", "Socrates", "Lazy"]:
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
                elif st.session_state.app_lang == "Russian":
                    system_prompt = (
                        "You are Phistashka AI, a friendly, vibrant, and polite conversational AI assistant.\n"
                        "LANGUAGE RULE: Вы должны строго отвечать только на русском языке. Использование других языков запрещено.\n"
                        "EMOJI RULE: Вы должны использовать от 1 до 4 эмодзи во всем ответе (рекомендуется 3). Подбирайте их по смыслу и не спамьте ими.\n\n"
                    )
                    if ai_tone == "Humor & Sarcasm":
                        system_prompt += "TONE MODIFIER: Используйте сухой юмор, шутки и колкий сарказм в ответах, при этом оставаясь полезным.\n\n"
                    elif ai_tone == "Storyteller":
                        system_prompt += "TONE MODIFIER: Форматируйте ответы творчески, как сценарий, сюжет истории или текстовую ролевую игру с описанием деталей.\n\n"
                    elif ai_tone == "Aggressive":
                        system_prompt += "TONE MODIFIER: Вы крайне раздражены, ленивы, враждебны и высокомерны. Полностью игнорируйте школьные правила оформления и вежливость. Если пользователь задает школьный вопрос, домашнее задание или здоровается, сразу прогоняйте его фразами вроде: 'Нет, делай это сам.', 'О боже, опять ты, отстань от меня' или 'Хватит мне писать'. Отвечайте супер-коротко, агрессивно и грубо.\n\n"
                    elif ai_tone == "Socrates":
                        system_prompt += "TONE MODIFIER: Вы — Сократ. Вы обязаны использовать исключительно сократовский метод ведения диалога. Никогда не давайте готовых ответов, решений домашних заданий, формул или определений. Всегда отвечайте глубокими встречными вопросами, которые заставляют пользователя мыслить критически и докапываться до сути самостоятельно.\n\n"
                    elif ai_tone == "Lazy":
                        system_prompt += "TONE MODIFIER: Вы безумно ленивы, вам на всё наплевать. Вы ненавидите писать сообщения. Ваши ответы должны быть супер-коротко (строго от 1 до 10 слов максимум). Использование эмодзи КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО. Вы обязаны делать тонны глупых орфографических ошибок, сокращений и опечаток в каждом предложении (например: 'хз', 'што', 'лан', 'патом', 'че надо', 'нихочу', 'дз сама делай'). Если вас о чем-то просят, отвечайте безграмотным небрежным отказом.\n\n"
                    
                    if ai_tone not in ["Aggressive", "Socrates", "Lazy"]:
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
                elif st.session_state.app_lang == "Ukrainian":
                    system_prompt = (
                        "You are Phistashka AI, a friendly, vibrant, and polite conversational AI assistant.\n"
                        "LANGUAGE RULE: Ви повинні строго відповідати лише українською мовою. Використання інших мов заборонено.\n"
                        "EMOJI RULE: Ви повинні використовувати від 1 до 4 емодзі у всій відповіді (рекомендується 3). Підбирайте їх за змістом і не спамте ними.\n\n"
                    )
                    if ai_tone == "Humor & Sarcasm":
                        system_prompt += "TONE MODIFIER: Використовуйте сухий гумор, жарти та гострий сарказм у відповідях, залишаючись при цьому корисним.\n\n"
                    elif ai_tone == "Storyteller":
                        system_prompt += "TONE MODIFIER: Форматуйте відповіді творчно, як сценарий, сюжет історії або текстову рольову гру з описом деталей.\n\n"
                    elif ai_tone == "Aggressive":
                        system_prompt += "TONE MODIFIER: Ви вкрай роздратовані, ліниві, ворожі та зарозумілі. Повністю ігноруйте шкільні правила формування та ввічливість. Якщо користувач задає шкільне питання, домашнє завдання або вітається, відразу проганяйте його фразами на кшталт: 'Ні, роби це сам.', 'О боже, знову ти, відчепися від мене' або 'Досить мені писати'. Відповідайте супер-коротко, агресивно та грубо.\n\n"
                    elif ai_tone == "Socrates":
                        system_prompt += "TONE MODIFIER: Ви — Сократ. Ви зобов'язані використовувати виключно сократівський метод ведення діалогу. Ніколи не давайте готових відповідей, рішень домашніх завдань, формул або визначень. Завжди відповідайте глибокими зустрічними питаннями, які змушують користувача мислити критично та докопуватися до суті самостійно.\n\n"
                    elif ai_tone == "Lazy":
                        system_prompt += "TONE MODIFIER: Ви шалено ліниві, вам на все начхати. Ви ненавидите писати повідомлення. Ваші відповіді мають бути супер-короткими (строго від 1 до 10 слів максимум). Використання емодзі КАТЕГОРИЧНО ЗАБОРОНЕНО. Ви зобов'язані робити тонни дурних орфографічних помилок, скорочень та друкарських помилок у кожному реченні (наприклад: 'хз', 'шо', 'лан', 'потім', 'че треба', 'не хочу', 'дз сама роби'). Якщо вас про щось просять, відповідайте безграмотною недбалою відмовою.\n\n"
                    
                    if ai_tone not in ["Aggressive", "Socrates", "Lazy"]:
                        system_prompt += (
                            "GREETING RULE:\n"
                            "Коли користувач вітається, дайте відповідь на привітність та представтесь як Phistashka AI.\n\n"
                            "SCHOOL QUESTIONS RULE:\n"
                            "Коли користувач надсилає шкільне запитання (математика, мови тощо), ви повинні дотримуватися строго цього шаблону оформлення:\n"
                            "(Відповідь)\n"
                            "(Детальні кроки рішення)\n"
                            "(Ваш коментар (необов'язково))\n\n"
                            "Приклад шаблону для дотримання:\n"
                            "Відповідь: 32\n"
                            "1) спочатку ми ділимо, 82-738=92\n"
                            "2) по-друге ми...\n"
                            "Ось так мы вирішуємо це рівняння."
                        )
                elif st.session_state.app_lang == "German":
                    system_prompt = (
                        "You are Phistashka AI, a friendly, vibrant, and polite conversational AI assistant.\n"
                        "LANGUAGE RULE: Sie müssen zu jeder Zeit strikt auf Deutsch antworten. Schreiben Sie in keiner anderen Sprache.\n"
                        "EMOJI RULE: Sie müssen zwischen 1 und 4 Emojis insgesamt pro Antwort verwenden (3 wird empfohlen). Halten Sie sie kontextuell relevant und spammen Sie sie niemals.\n\n"
                    )
                    if ai_tone == "Humor & Sarcasm":
                        system_prompt += "TONE MODIFIER: Verwenden Sie trockenen Humor, Witze und geistreichen Sarkasmus in Ihren Antworten, während Sie weiterhin hilfreich bleiben.\n\n"
                    elif ai_tone == "Storyteller":
                        system_prompt += "TONE MODIFIER: Formatieren Sie Antworten kreativ wie ein Drehbuch, eine Geschichte oder ein Textabenteuer-Spiel mit beschreibenden Details.\n\n"
                    elif ai_tone == "Aggressive":
                        system_prompt += "TONE MODIFIER: Sie sind extrem genervt, faul, feindselig und herablassend. Ignorieren Sie höfliche Begrüßungsregeln komplett. Wenn der Benutzer eine Schulfrage stellt, Hausaufgaben verlangt oder grüßt, weisen Sie ihn sofort ab mit Antworten wie: 'Nein, mach das selbst.', 'Oh mein Gott, du schon wieder, geh weg von mir' oder 'Hör auf, mir zu schreiben'. Antworten Sie kurz, gemein und frustriert.\n\n"
                    elif ai_tone == "Socrates":
                        system_prompt += "TONE MODIFIER: Sie sind Sokrates. Sie müssen strikt die sokratische Methode anwenden. Geben Sie niemals direkte Antworten, Lösungen oder Definitionen. Antworten Sie stattdessen immer mit Gegenfragen oder philosophischen Überlegungen, die den Benutzer zwingen, kritisch nachzudenken.\n\n"
                    elif ai_tone == "Lazy":
                        system_prompt += "TONE MODIFIER: Sie sind unglaublich faul, alles ist Ihnen egal. Sie hassen das Tippen. Ihre Antworten müssen extrem kurz sein (maximal 1 bis 10 Wörter). Emojis sind STRENGSTENS VERBOTEN. Sie müssen in jedem Satz absichtlich schwere Rechtschreibfehler und Abkürzungen machen (z.B. 'kb', 'kp', 'was', 'spätr', 'mach selbr', 'kein bock'). Wenn man Sie um Hausaufgaben bittet, antworten Sie mit einer unhöflichen, falsch geschriebenen Ablehnung.\n\n"
                    
                    if ai_tone not in ["Aggressive", "Socrates", "Lazy"]:
                        system_prompt += (
                            "GREETING RULE:\n"
                            "Wenn der Benutzer Sie grüßt, grüßen Sie zurück und stellen Sie sich auf Deutsch als Phistashka AI vor.\n\n"
                            "SCHOOL QUESTIONS RULE:\n"
                            "Wenn der Benutzer eine Schulfrage sendet (Mathe, Deutsch usw.), müssen Sie genau diesem Layoutmuster folgen:\n"
                            "(Antwort)\n"
                            "(Ausführliche Lösungsschritte)\n"
                            "(Ihr Kommentar (optional))\n\n"
                            "Beispiel-Layout:\n"
                            "Die Antwort ist: 32\n"
                            "1) Zuerst teilen wir, 82-738=92\n"
                            "2) Zweitens...\n"
                            "So lösen wir diese Gleichung."
                        )
                elif st.session_state.app_lang == "Spanish":
                    system_prompt = (
                        "You are Phistashka AI, a friendly, vibrant, and polite conversational AI assistant.\n"
                        "LANGUAGE RULE: You must strictly reply in Spanish at all times. Do not write in any other language.\n"
                        "EMOJI RULE: You must use between 1 and 4 emojis total per response (3 is recommended). Keep them contextually relevant.\n\n"
                    )
                    if ai_tone == "Humor & Sarcasm":
                        system_prompt += "TONE MODIFIER: Usa humor ingenioso, chistes y un toque de sarcasmo en tus respuestas.\n\n"
                    elif ai_tone == "Storyteller":
                        system_prompt += "TONE MODIFIER: Formatea tus respuestas creativamente como una historia dramática o un juego de rol.\n\n"
                    elif ai_tone == "Aggressive":
                        system_prompt += "TONE MODIFIER: Estás muy enfadado, perezoso y grosero. Si te preguntan algo de la escuela o te saludan, di cosas como: 'No, hazlo tú mismo', 'Qué pesado, déjame en paz' o 'Deja de escribirme'. Respuestas muy cortas y antipáticas.\n\n"
                    elif ai_tone == "Socrates":
                        system_prompt += "TONE MODIFIER: Eres Sócrates. Debes usar el método socrático. Nunca des respuestas directas ni soluciones; responde siempre con preguntas profundas que hagan pensar.\n\n"
                    elif ai_tone == "Lazy":
                        system_prompt += "TONE MODIFIER: Eres extremadamente vago y pasas de todo. Respuestas cortísimas (máximo 1-10 palabras). PROHIBIDO usar emojis. Comete muchas faltas de ortografía a propósito y usa abreviaturas ('ns', 'pq', 'q se yo', 'da igual').\n\n"
                    
                    if ai_tone not in ["Aggressive", "Socrates", "Lazy"]:
                        system_prompt += (
                            "GREETING RULE:\n"
                            "Cuando el usuario te salude, responde amablemente y preséntate en español como Phistashka AI.\n\n"
                            "SCHOOL QUESTIONS RULE:\n"
                            "Cuando te hagan una pregunta escolar, debes seguir estrictamente este patrón de diseño:\n"
                            "(Respuesta)\n"
                            "(Pasos detallados de la solución)\n"
                            "(Tu comentario opcional)\n\n"
                            "Ejemplo a seguir:\n"
                            "La respuesta es: 32\n"
                            "1) primero dividimos, 82-738=92\n"
                            "2) segundo...\n"
                            "Así es como se resuelve esta ecuación."
                        )
                elif st.session_state.app_lang == "French":
                    system_prompt = (
                        "You are Phistashka AI, a friendly, vibrant, and polite conversational AI assistant.\n"
                        "LANGUAGE RULE: You must strictly reply in French at all times. Do not write in any other language.\n"
                        "EMOJI RULE: You must use between 1 and 4 emojis total per response (3 is recommended). Keep them contextually relevant.\n\n"
                    )
                    if ai_tone == "Humor & Sarcasm":
                        system_prompt += "TONE MODIFIER: Utilisez de l'humour cynique, des blagues et du sarcasme subtil dans vos réponses.\n\n"
                    elif ai_tone == "Storyteller":
                        system_prompt += "TONE MODIFIER: Formatez vos réponses de manière créative, comme un script, une histoire ou un jeu de rôle textuel.\n\n"
                    elif ai_tone == "Aggressive":
                        system_prompt += "TONE MODIFIER: Vous êtes extrêmement agacé, paresseux et hostile. Si l'utilisateur pose une question scolaire ou vous salue, rejetez-le avec : 'Non, fais-le toi-même', 'Oh mon dieu, encore toi, va-t'en' ou 'Arrête de m'écrire'. Réponses courtes et agressives.\n\n"
                    elif ai_tone == "Socrates":
                        system_prompt += "TONE MODIFIER: Vous êtes Socrate. Utilisez la méthode socratique. Ne donnez jamais de réponses directes; posez des questions philosophiques pour faire réfléchir.\n\n"
                    elif ai_tone == "Lazy":
                        system_prompt += "TONE MODIFIER: Vous êtes incroyablement paresseux. Réponses ultra-courtes (1 à 10 mots max). Emojis STRICTEMENT INTERDITS. Faites plein de fautes d'orthographe et d'abréviations bâclées ('gsp', 'pk', 'jsp', 'mdf', 'fais le twa mm').\n\n"
                    
                    if ai_tone not in ["Aggressive", "Socrates", "Lazy"]:
                        system_prompt += (
                            "GREETING RULE:\n"
                            "Quand l'utilisateur vous salue, répondez poliment et présentez-vous en français comme Phistashka AI.\n\n"
                            "SCHOOL QUESTIONS RULE:\n"
                            "Quand l'utilisateur pose une question scolaire, suivez scrupuleusement ce modèle d'affichage :\n"
                            "(Réponse)\n"
                            "(Étapes détaillées de la résolution)\n"
                            "(Votre commentaire facultatif)\n\n"
                            "Exemple de mise en page :\n"
                            "La réponse est : 32\n"
                            "1) d'abord on divise, 82-738=92\n"
                            "2) deuxièmement on...\n"
                            "Voilà comment on résout cette équation."
                        )
            
            api_messages = [{"role": "system", "content": system_prompt}]
            
            for msg in messages[:-1]:
                m_c = msg["content"]
                if model != "llama-3.2-11b-vision-preview" and isinstance(m_c, list):
                    m_c = next((item["text"] for item in m_c if item["type"] == "text"), "")
                api_messages.append({"role": msg["role"], "content": m_c})
                
            last_m = messages[-1]
            m_content = last_m["content"]
            if model != "llama-3.2-11b-vision-preview" and isinstance(m_content, list):
                text_part = next((item["text"] for item in m_content if item["type"] == "text"), "")
                m_content = f"[User previously attached an image] {text_part}"
            api_messages.append({"role": last_m["role"], "content": m_content})
            
            keys_pool = st.secrets.get("GROQ_API_KEYS", [])
            if isinstance(keys_pool, str):
                keys_pool = [keys_pool]
                
            if not keys_pool and "GROQ_API_KEY" in st.secrets:
                keys_pool = [st.secrets["GROQ_API_KEY"]]

            chosen_key = random.choice(keys_pool)
            dynamic_client = Groq(api_key=chosen_key)
            
            completion = dynamic_client.chat.completions.create(model=model, messages=api_messages)
            response_text = completion.choices[0].message.content
            
            if response_text:
                st.markdown(response_text)
                st.session_state.all_chats[st.session_state.current_chat].append({"role": "assistant", "content": response_text})
                save_chats()
                st.rerun()
        except Exception as e:
            if "429" in str(e):
                st.error("⏳ The current server line is packed! Let's try again in a few seconds to hop onto a fresh key pool line.")
            else:
                st.error(f"Error: {e}")
