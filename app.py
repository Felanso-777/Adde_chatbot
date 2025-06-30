import streamlit as st
import requests

# 🔐 Hugging Face Token
HF_TOKEN = st.secrets["HF_TOKEN"]
 # Replace with your token
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# 📤 API call to Hugging Face
def query_huggingface(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "do_sample": True
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    try:
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        elif isinstance(result, dict) and "error" in result:
            return f"❌ API Error: {result['error']}"
        else:
            return f"⚠️ Unexpected API response: {result}"
    except requests.exceptions.JSONDecodeError:
        return f"❌ Invalid response: {response.text}"

# 🌙 Streamlit config
st.set_page_config(page_title="Adde Chatbot", layout="centered")

# 🌌 Custom CSS
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .message {
        padding: 10px;
        margin: 5px 0;
        border-radius: 12px;
    }
    .user {
        background-color: #1f2937;
        text-align: right;
        color: #d1fae5;
    }
    .bot {
        background-color: #374151;
        text-align: left;
        color: #e5e7eb;
    }
    .chat-input {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #0e1117;
        padding: 10px;
        z-index: 9999;
        display: flex;
        gap: 10px;
    }
    input[type="text"] {
        flex-grow: 1;
        padding: 10px;
        border-radius: 8px;
        border: none;
        background-color: #1e1e1e;
        color: white;
        font-size: 16px;
    }
    button {
        background-color: #4b4b4b;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💬 Adde Chatbot (Zephyr AI)")

# 💬 Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# 📜 Display messages
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "bot"
    st.markdown(f"<div class='message {role_class}'>{msg['content']}</div>", unsafe_allow_html=True)

# 📥 Chat input at the bottom using HTML
with st.form(key="chat_form", clear_on_submit=True):
    st.markdown("<div class='chat-input'>", unsafe_allow_html=True)
    user_input = st.text_input("", placeholder="Type your message...", label_visibility="collapsed")
    send_btn = st.form_submit_button("Send")
    st.markdown("</div>", unsafe_allow_html=True)

# 🤖 Process message
if send_btn and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Create prompt from conversation
    prompt = ""
    for msg in st.session_state.messages:
        speaker = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{speaker}: {msg['content']}\n"
    prompt += "Assistant:"

    # Get response
    bot_output = query_huggingface(prompt)

    if bot_output.startswith(prompt):
        reply = bot_output[len(prompt):].strip().split("\n")[0]
    else:
        reply = bot_output

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
