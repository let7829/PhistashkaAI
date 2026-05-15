import streamlit as st
from groq import Groq
import base64
import streamlit.components.v1 as components

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.markdown("""
    <style>
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}

    .stChatInputContainer > div {
        margin-left: 55px !important;
    }

    .stPopover {
        position: fixed;
        bottom: 34px;
        left: 10px;
        z-index: 9999;
    }
    
    .stPopover > button {
        border-radius: 12px !important;
        width: 44px !important;
        height: 44px !important;
        background-color: #1e1f26 !important;
        border: 1.5px solid #464b5d !important;
        font-weight: bold !important;
        color: white !important;
        font-size: 20px !important;
        padding: 0 !important;
        line-height: 1 !important;
    }
    
    div[data-testid="stPopoverBody"] {
        position: fixed !important;
        top: auto !important;
        bottom: 90px !important;
        left: 10px !important;
        right: auto !important;
        width: 320px !important;
        max-height: 400px !important;
        background: #1e1f26 !important;
        border: 1px solid #464b5d !important;
        border-radius: 14px !important;
        padding: 12px !important;
        z-index: 99999 !important;
        overflow-y: auto !important;
    }
    </style>
""", unsafe_allow_html=True)

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"
if "pending_image_b64" not in st.session_state:
    st.session_state.pending_image_b64 = None
if "pending_image_name" not in st.session_state:
    st.session_state.pending_image_name = None
if "pending_doc_text" not in st.session_state:
    st.session_state.pending_doc_text = None

with st.sidebar:
    st.header("Chats")
    if st.button("New Chat"):
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

if st.session_state.pending_image_b64:
    st.info(f"🖼️ Image ready: {st.session_state.pending_image_name}")
if st.session_state.pending_doc_text:
    st.info("📄 File attached — send your message!")

picker_result = components.declare_component(
    "file_picker",
    url=None
) if False else None

PICKER_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; font-family: sans-serif; }
body { background: transparent; color: white; padding: 4px; }

.tabs {
    display: flex;
    gap: 6px;
    margin-bottom: 10px;
}
.tab {
    flex: 1;
    padding: 7px;
    border-radius: 8px;
    border: 1px solid #464b5d;
    background: #2a2b35;
    color: #aaa;
    cursor: pointer;
    font-size: 13px;
    text-align: center;
}
.tab.active {
    background: #3a3d52;
    color: white;
    border-color: #6c72a8;
}

#imageSection, #fileSection { display: none; }
#imageSection.visible, #fileSection.visible { display: block; }

.gallery {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 5px;
    max-height: 200px;
    overflow-y: auto;
    margin-bottom: 8px;
}
.gallery img {
    width: 100%;
    aspect-ratio: 1;
    object-fit: cover;
    border-radius: 6px;
    cursor: pointer;
    border: 2px solid transparent;
    transition: border 0.15s;
}
.gallery img.selected {
    border-color: #6c72a8;
}

.btn {
    width: 100%;
    padding: 8px;
    border-radius: 8px;
    border: 1px solid #464b5d;
    background: #2a2b35;
    color: white;
    cursor: pointer;
    font-size: 13px;
    margin-bottom: 6px;
}
.btn:hover { background: #3a3d52; }
.btn.confirm {
    background: #4a4f7a;
    border-color: #6c72a8;
    font-weight: bold;
}
.btn.confirm:hover { background: #5a60a0; }

.status {
    font-size: 11px;
    color: #888;
    text-align: center;
    margin: 4px 0;
    min-height: 16px;
}
.error { color: #e57373; }
.success { color: #81c784; }

#fileList {
    max-height: 160px;
    overflow-y: auto;
    margin-bottom: 8px;
}
.file-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 6px;
    cursor: pointer;
    border: 1px solid transparent;
    transition: background 0.1s;
}
.file-item:hover { background: #2a2b35; }
.file-item.selected { background: #3a3d52; border-color: #6c72a8; }
.file-item .icon { font-size: 18px; }
.file-item .name { font-size: 12px; color: #ccc; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
</head>
<body>

<div class="tabs">
    <div class="tab active" id="tabImg" onclick="switchTab('image')">🖼️ Images</div>
    <div class="tab" id="tabFile" onclick="switchTab('file')">📁 Files</div>
</div>

<div id="imageSection" class="visible">
    <button class="btn" onclick="loadGallery()">📂 Open Image Gallery</button>
    <div class="status" id="imgStatus"></div>
    <div class="gallery" id="gallery"></div>
    <button class="btn confirm" id="confirmImg" style="display:none" onclick="confirmImage()">✓ Attach Image</button>
</div>

<div id="fileSection">
    <button class="btn" onclick="openFilePicker()">📂 Browse Files</button>
    <div class="status" id="fileStatus"></div>
    <div id="fileList"></div>
    <button class="btn confirm" id="confirmFile" style="display:none" onclick="confirmFile()">✓ Attach File</button>
</div>

<script>
let selectedImageB64 = null;
let selectedImageName = null;
let selectedFileText = null;
let selectedFileName = null;
let selectedImgEl = null;

function switchTab(tab) {
    document.getElementById('tabImg').classList.toggle('active', tab === 'image');
    document.getElementById('tabFile').classList.toggle('active', tab === 'file');
    document.getElementById('imageSection').classList.toggle('visible', tab === 'image');
    document.getElementById('fileSection').classList.toggle('visible', tab === 'file');
}

async function loadGallery() {
    const status = document.getElementById('imgStatus');
    const gallery = document.getElementById('gallery');
    gallery.innerHTML = '';
    document.getElementById('confirmImg').style.display = 'none';
    selectedImageB64 = null;

    try {
        let handles;
        if (window.showOpenFilePicker) {
            handles = await window.showOpenFilePicker({
                multiple: true,
                types: [{ description: 'Images', accept: { 'image/*': ['.png','.jpg','.jpeg','.gif','.webp'] } }]
            });
        } else {
            fallbackImagePicker();
            return;
        }

        if (!handles.length) { status.textContent = ''; return; }
        status.textContent = `${handles.length} image(s) loaded`;
        status.className = 'status success';

        for (const handle of handles) {
            const file = await handle.getFile();
            const reader = new FileReader();
            reader.onload = (e) => {
                const b64 = e.target.result.split(',')[1];
                const name = file.name;
                const img = document.createElement('img');
                img.src = e.target.result;
                img.title = name;
                img.onclick = () => {
                    if (selectedImgEl) selectedImgEl.classList.remove('selected');
                    img.classList.add('selected');
                    selectedImgEl = img;
                    selectedImageB64 = b64;
                    selectedImageName = name;
                    document.getElementById('confirmImg').style.display = 'block';
                };
                gallery.appendChild(img);
            };
            reader.readAsDataURL(file);
        }
    } catch(e) {
        if (e.name === 'AbortError') { status.textContent = ''; return; }
        if (e.name === 'SecurityError' || e.name === 'NotAllowedError') {
            status.innerHTML = '⛔ No file access. Allow file access to upload.';
            status.className = 'status error';
        } else {
            fallbackImagePicker();
        }
    }
}

function fallbackImagePicker() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.multiple = true;
    input.onchange = () => {
        const gallery = document.getElementById('gallery');
        gallery.innerHTML = '';
        const files = Array.from(input.files);
        const status = document.getElementById('imgStatus');
        status.textContent = `${files.length} image(s) loaded`;
        status.className = 'status success';
        files.forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const b64 = e.target.result.split(',')[1];
                const img = document.createElement('img');
                img.src = e.target.result;
                img.title = file.name;
                img.onclick = () => {
                    if (selectedImgEl) selectedImgEl.classList.remove('selected');
                    img.classList.add('selected');
                    selectedImgEl = img;
                    selectedImageB64 = b64;
                    selectedImageName = file.name;
                    document.getElementById('confirmImg').style.display = 'block';
                };
                gallery.appendChild(img);
            };
            reader.readAsDataURL(file);
        });
    };
    input.click();
}

function confirmImage() {
    if (!selectedImageB64) return;
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        value: { kind: 'image', b64: selectedImageB64, name: selectedImageName }
    }, '*');
    document.getElementById('imgStatus').textContent = '✓ Attached! Send your message.';
    document.getElementById('imgStatus').className = 'status success';
}

async function openFilePicker() {
    const status = document.getElementById('fileStatus');
    const list = document.getElementById('fileList');
    list.innerHTML = '';
    document.getElementById('confirmFile').style.display = 'none';
    selectedFileText = null;

    try {
        let handles;
        if (window.showOpenFilePicker) {
            handles = await window.showOpenFilePicker({ multiple: false });
        } else {
            fallbackFilePicker();
            return;
        }

        const handle = handles[0];
        const file = await handle.getFile();
        readFileItem(file);
    } catch(e) {
        if (e.name === 'AbortError') { status.textContent = ''; return; }
        if (e.name === 'SecurityError' || e.name === 'NotAllowedError') {
            status.innerHTML = '⛔ No file access. Allow file access to upload.';
            status.className = 'status error';
        } else {
            fallbackFilePicker();
        }
    }
}

function fallbackFilePicker() {
    const input = document.createElement('input');
    input.type = 'file';
    input.onchange = () => { if (input.files[0]) readFileItem(input.files[0]); };
    input.click();
}

function readFileItem(file) {
    const list = document.getElementById('fileList');
    const status = document.getElementById('fileStatus');
    list.innerHTML = '';

    const ext = file.name.split('.').pop().toLowerCase();
    const icons = { pdf: '📄', txt: '📝', py: '🐍', js: '📜', json: '🗂️', csv: '📊', md: '📋' };
    const icon = icons[ext] || '📁';

    const item = document.createElement('div');
    item.className = 'file-item selected';
    item.innerHTML = `<span class="icon">${icon}</span><span class="name">${file.name}</span>`;
    list.appendChild(item);

    const reader = new FileReader();
    reader.onload = (e) => {
        selectedFileText = `[File: ${file.name}]\n${e.target.result}`;
        selectedFileName = file.name;
        document.getElementById('confirmFile').style.display = 'block';
        status.textContent = `${file.name} (${(file.size/1024).toFixed(1)} KB)`;
        status.className = 'status success';
    };
    reader.onerror = () => {
        selectedFileText = `[Attached file: ${file.name}]`;
        selectedFileName = file.name;
        document.getElementById('confirmFile').style.display = 'block';
    };
    reader.readAsText(file);
}

function confirmFile() {
    if (!selectedFileText) return;
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        value: { kind: 'file', text: selectedFileText, name: selectedFileName }
    }, '*');
    document.getElementById('fileStatus').textContent = '✓ Attached! Send your message.';
    document.getElementById('fileStatus').className = 'status success';
}
</script>
</body>
</html>
"""

with st.popover("➕"):
    result = components.html(PICKER_HTML, height=320, scrolling=False)
    if result and isinstance(result, dict):
        if result.get("kind") == "image":
            st.session_state.pending_image_b64 = result["b64"]
            st.session_state.pending_image_name = result["name"]
        elif result.get("kind") == "file":
            st.session_state.pending_doc_text = result["text"]

prompt = st.chat_input("Say hello!")

if prompt:
    image_b64 = st.session_state.pending_image_b64
    context_info = st.session_state.pending_doc_text or ""

    messages.append({
        "role": "user",
        "content": prompt + ("\n\n" + context_info if context_info else ""),
        "image_b64": image_b64
    })

    st.session_state.pending_image_b64 = None
    st.session_state.pending_image_name = None
    st.session_state.pending_doc_
