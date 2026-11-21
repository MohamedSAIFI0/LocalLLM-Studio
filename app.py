import streamlit as st
import ollama
import json
import uuid
import re
import time
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ENSET Chatbot", layout="wide")
st.title("ENSET Chatbot")

available_models = ["llama3.2:latest", "qwen2.5:0.5b"]

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

if "comparison_history" not in st.session_state:
    st.session_state.comparison_history = []

if st.session_state.current_conv_id not in st.session_state.conversations:
    if st.session_state.conversations:
        st.session_state.current_conv_id = next(iter(st.session_state.conversations.keys()))
    else:
        new_id, new_conv = init_conversation()
        st.session_state.conversations[new_id] = new_conv
        st.session_state.current_conv_id = new_id

mode = st.sidebar.radio(
    "Mode de fonctionnement",
    ["Chatbot", "Comparaison des modèles"]
)

if mode == "Chatbot":
    st.sidebar.markdown("---")
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
            if "metrics" in message:
                m = message["metrics"]
                st.caption(f"Temps de réponse: {m['total_time']}s | TTFT: {m['ttft']}s | Tokens: {m['tokens']} | Vitesse: {m['speed']} tokens/s")

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
            start_time = time.time()
            ttft = None
            eval_count = 0

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
                    chunk = response.get("message", {}).get("content", "")
                    if chunk:
                        if ttft is None:
                            ttft = time.time() - start_time
                        full_response += chunk
                        message_placeholder.markdown(full_response)
                    if response.get("done") and response.get("eval_count") is not None:
                        eval_count = response.get("eval_count")

                end_time = time.time()
                total_time = end_time - start_time
                if ttft is None:
                    ttft = total_time
                if eval_count == 0:
                    eval_count = max(1, len(full_response.split()))
                speed = eval_count / total_time if total_time > 0 else 0.0

                message_placeholder.markdown(full_response)
                metrics_data = {
                    "total_time": round(total_time, 2),
                    "ttft": round(ttft, 2),
                    "tokens": eval_count,
                    "speed": round(speed, 2)
                }
                st.caption(f"Temps de réponse: {metrics_data['total_time']}s | TTFT: {metrics_data['ttft']}s | Tokens: {metrics_data['tokens']} | Vitesse: {metrics_data['speed']} tokens/s")

                current_messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "metrics": metrics_data
                })

            except Exception as e:
                st.error(f"Erreur Ollama : {e}")

else:
    st.subheader("Comparaison des modèles")

    st.sidebar.markdown("---")
    st.sidebar.header("Paramètres de génération")

    temperature = st.sidebar.slider(
        "Température",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        key="compare_temp"
    )

    top_k = st.sidebar.slider(
        "Top-k",
        min_value=1,
        max_value=100,
        value=40,
        step=1,
        key="compare_top_k"
    )

    top_p = st.sidebar.slider(
        "Top-p",
        min_value=0.0,
        max_value=1.0,
        value=0.9,
        step=0.05,
        key="compare_top_p"
    )

    max_tokens = st.sidebar.slider(
        "Nombre maximal de tokens",
        min_value=1,
        max_value=2048,
        value=512,
        step=1,
        key="compare_max_tokens"
    )

    if st.sidebar.button("Effacer l'historique de comparaison", use_container_width=True):
        st.session_state.comparison_history = []
        st.rerun()

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        model_1 = st.selectbox(
            "Sélectionner le modèle 1",
            available_models,
            index=0,
            key="compare_m1"
        )
    with col_m2:
        model_2 = st.selectbox(
            "Sélectionner le modèle 2",
            available_models,
            index=1 if len(available_models) > 1 else 0,
            key="compare_m2"
        )

    for item in st.session_state.comparison_history:
        st.markdown(f"**Question :** {item['prompt']}")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Modèle 1 : {item['model_1']}**")
            st.markdown(item['response_1'])
        with c2:
            st.markdown(f"**Modèle 2 : {item['model_2']}**")
            st.markdown(item['response_2'])

        st.markdown("**Tableau comparatif des performances**")
        df_metrics = pd.DataFrame({
            "Indicateur": [
                "Temps de réponse (s)",
                "Temps premier token (TTFT) (s)",
                "Nombre de tokens générés",
                "Vitesse de génération (tokens/s)"
            ],
            f"Modèle 1 ({item['model_1']})": [
                f"{item['metrics_1']['total_time']:.2f}",
                f"{item['metrics_1']['ttft']:.2f}",
                item['metrics_1']['tokens'],
                f"{item['metrics_1']['speed']:.2f}"
            ],
            f"Modèle 2 ({item['model_2']})": [
                f"{item['metrics_2']['total_time']:.2f}",
                f"{item['metrics_2']['ttft']:.2f}",
                item['metrics_2']['tokens'],
                f"{item['metrics_2']['speed']:.2f}"
            ]
        })
        st.dataframe(df_metrics, use_container_width=True, hide_index=True)

        st.markdown("**Analyse graphique des performances**")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.caption("Vitesse de génération (tokens/s)")
            chart_speed = pd.DataFrame({
                "Modèle": [f"Modèle 1 ({item['model_1']})", f"Modèle 2 ({item['model_2']})"],
                "Tokens / seconde": [item['metrics_1']['speed'], item['metrics_2']['speed']]
            }).set_index("Modèle")
            st.bar_chart(chart_speed)

        with col_g2:
            st.caption("Durées : Temps de réponse total et TTFT (secondes)")
            chart_times = pd.DataFrame({
                "Modèle": [f"Modèle 1 ({item['model_1']})", f"Modèle 2 ({item['model_2']})"],
                "Temps total (s)": [item['metrics_1']['total_time'], item['metrics_2']['total_time']],
                "TTFT (s)": [item['metrics_1']['ttft'], item['metrics_2']['ttft']]
            }).set_index("Modèle")
            st.bar_chart(chart_times)

        st.markdown("---")

    prompt = st.chat_input("Saisissez une question unique à envoyer aux deux modèles...")

    if prompt:
        st.markdown(f"**Question :** {prompt}")
        col1, col2 = st.columns(2)

        shared_options = {
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "num_predict": max_tokens,
        }

        with col1:
            st.markdown(f"**Modèle 1 : {model_1}**")
            placeholder_1 = st.empty()
            full_resp_1 = ""
            start_time_1 = time.time()
            ttft_1 = None
            eval_count_1 = 0
            try:
                for response in ollama.chat(
                    model=model_1,
                    messages=[{"role": "user", "content": prompt}],
                    options=shared_options,
                    stream=True
                ):
                    chunk = response.get("message", {}).get("content", "")
                    if chunk:
                        if ttft_1 is None:
                            ttft_1 = time.time() - start_time_1
                        full_resp_1 += chunk
                        placeholder_1.markdown(full_resp_1)
                    if response.get("done") and response.get("eval_count") is not None:
                        eval_count_1 = response.get("eval_count")

                end_time_1 = time.time()
                total_time_1 = end_time_1 - start_time_1
                if ttft_1 is None:
                    ttft_1 = total_time_1
                if eval_count_1 == 0:
                    eval_count_1 = max(1, len(full_resp_1.split()))
                speed_1 = eval_count_1 / total_time_1 if total_time_1 > 0 else 0.0

                placeholder_1.markdown(full_resp_1)
                metrics_1 = {
                    "total_time": round(total_time_1, 2),
                    "ttft": round(ttft_1, 2),
                    "tokens": eval_count_1,
                    "speed": round(speed_1, 2)
                }
            except Exception as e:
                placeholder_1.error(f"Erreur {model_1} : {e}")
                metrics_1 = {"total_time": 0.0, "ttft": 0.0, "tokens": 0, "speed": 0.0}

        with col2:
            st.markdown(f"**Modèle 2 : {model_2}**")
            placeholder_2 = st.empty()
            full_resp_2 = ""
            start_time_2 = time.time()
            ttft_2 = None
            eval_count_2 = 0
            try:
                for response in ollama.chat(
                    model=model_2,
                    messages=[{"role": "user", "content": prompt}],
                    options=shared_options,
                    stream=True
                ):
                    chunk = response.get("message", {}).get("content", "")
                    if chunk:
                        if ttft_2 is None:
                            ttft_2 = time.time() - start_time_2
                        full_resp_2 += chunk
                        placeholder_2.markdown(full_resp_2)
                    if response.get("done") and response.get("eval_count") is not None:
                        eval_count_2 = response.get("eval_count")

                end_time_2 = time.time()
                total_time_2 = end_time_2 - start_time_2
                if ttft_2 is None:
                    ttft_2 = total_time_2
                if eval_count_2 == 0:
                    eval_count_2 = max(1, len(full_resp_2.split()))
                speed_2 = eval_count_2 / total_time_2 if total_time_2 > 0 else 0.0

                placeholder_2.markdown(full_resp_2)
                metrics_2 = {
                    "total_time": round(total_time_2, 2),
                    "ttft": round(ttft_2, 2),
                    "tokens": eval_count_2,
                    "speed": round(speed_2, 2)
                }
            except Exception as e:
                placeholder_2.error(f"Erreur {model_2} : {e}")
                metrics_2 = {"total_time": 0.0, "ttft": 0.0, "tokens": 0, "speed": 0.0}

        st.session_state.comparison_history.append({
            "prompt": prompt,
            "model_1": model_1,
            "response_1": full_resp_1,
            "metrics_1": metrics_1,
            "model_2": model_2,
            "response_2": full_resp_2,
            "metrics_2": metrics_2
        })
        st.rerun()
