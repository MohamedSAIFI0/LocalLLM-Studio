import streamlit as st
import ollama
import json
import uuid
import re
from datetime import datetime

st.set_page_config(page_title="ENSET Chatbot", layout="wide")
st.title("ENSET Chatbot")

def init_conversation():
    new_id = str(uuid.uuid4())
    conv_number = len(st.session_state.get("conversations", {})) + 1
    return new_id, {
        "title": f"Conversation {conv_number}",
        "messages": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

if "conversations" not in st.session_state:
    st.session_state.conversations = {}
    first_id, first_conv = init_conversation()
    st.session_state.conversations[first_id] = first_conv
    st.session_state.current_conv_id = first_id

if st.session_state.current_conv_id not in st.session_state.conversations:
    if st.session_state.conversations:
        st.session_state.current_conv_id = next(iter(st.session_state.conversations.keys()))
    else:
        new_id, new_conv = init_conversation()
        st.session_state.conversations[new_id] = new_conv
        st.session_state.current_conv_id = new_id

st.sidebar.header("Gestion des conversations")

if st.sidebar.button("Nouvelle conversation", use_container_width=True):
    new_id, new_conv = init_conversation()
    st.session_state.conversations[new_id] = new_conv
    st.session_state.current_conv_id = new_id
    st.rerun()

conv_keys = list(st.session_state.conversations.keys())
current_index = conv_keys.index(st.session_state.current_conv_id) if st.session_state.current_conv_id in conv_keys else 0

selected_conv_id = st.sidebar.selectbox(
    "Sélectionner une conversation",
    options=conv_keys,
    index=current_index,
    format_func=lambda cid: st.session_state.conversations[cid]["title"]
)

if selected_conv_id != st.session_state.current_conv_id:
    st.session_state.current_conv_id = selected_conv_id
    st.rerun()

if st.sidebar.button("Supprimer la conversation", use_container_width=True):
    del st.session_state.conversations[st.session_state.current_conv_id]
    if not st.session_state.conversations:
        new_id, new_conv = init_conversation()
        st.session_state.conversations[new_id] = new_conv
        st.session_state.current_conv_id = new_id
    else:
        st.session_state.current_conv_id = next(iter(st.session_state.conversations.keys()))
    st.rerun()

current_conv = st.session_state.conversations[st.session_state.current_conv_id]
current_messages = current_conv["messages"]

st.sidebar.markdown("---")
st.sidebar.subheader("Télécharger l'historique")

txt_export = f"=== Historique : {current_conv['title']} ===\n"
txt_export += f"Date de création : {current_conv.get('created_at', 'N/A')}\n"
txt_export += "-" * 40 + "\n\n"
for msg in current_messages:
    speaker = "Utilisateur" if msg["role"] == "user" else "Assistant"
    txt_export += f"[{speaker}] :\n{msg['content']}\n\n"

json_export = json.dumps({
    "title": current_conv["title"],
    "created_at": current_conv.get("created_at", ""),
    "messages": current_messages
}, ensure_ascii=False, indent=2)

clean_title = re.sub(r'[^\w\-_\.]', '_', current_conv['title']).lower()

col_txt, col_json = st.sidebar.columns(2)
with col_txt:
    st.download_button(
        label="Format TXT",
        data=txt_export,
        file_name=f"{clean_title}.txt",
        mime="text/plain",
        use_container_width=True
    )

with col_json:
    st.download_button(
        label="Format JSON",
        data=json_export,
        file_name=f"{clean_title}.json",
        mime="application/json",
        use_container_width=True
    )

st.sidebar.markdown("---")
st.sidebar.header("Options de configuration")

available_models = ["llama3.2:latest", "qwen2.5:0.5b"]
selected_model = st.sidebar.selectbox(
    "Modèle",
    available_models,
    index=0
)

temperature = st.sidebar.slider(
    "Température",
    min_value=0.0,
    max_value=2.0,
    value=0.7,
    step=0.1
)

top_k = st.sidebar.slider(
    "Top-k",
    min_value=1,
    max_value=100,
    value=40,
    step=1
)

top_p = st.sidebar.slider(
    "Top-p",
    min_value=0.0,
    max_value=1.0,
    value=0.9,
    step=0.05
)

max_tokens = st.sidebar.slider(
    "Nombre maximal de tokens",
    min_value=1,
    max_value=2048,
    value=512,
    step=1
)

st.subheader(current_conv['title'])

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Que voulez-vous me demander ?")

if prompt:
    if len(current_messages) == 0 and current_conv["title"].startswith("Conversation"):
        current_conv["title"] = (prompt[:30] + "...") if len(prompt) > 30 else prompt

    with st.chat_message("user"):
        st.markdown(prompt)

    current_messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            for response in ollama.chat(
                model=selected_model,
                messages=current_messages,
                options={
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                    "num_predict": max_tokens,
                },
                stream=True
            ):
                full_response += response["message"]["content"]
                message_placeholder.markdown(full_response)

            message_placeholder.markdown(full_response)

            current_messages.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            st.error(f"Erreur Ollama : {e}")
