
import streamlit as st
import ollama

st.title("ENSET Chatbot")

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

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Que voulez-vous me demander ?")

if prompt:

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("assistant"):

        message_placeholder = st.empty()
        full_response = ""

        try:
            for response in ollama.chat(
                model=selected_model,
                messages=st.session_state.messages,
                options={
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                    "num_predict": max_tokens,
                },
                stream=True
            ):

                full_response += response["message"]["content"]

                message_placeholder.markdown(
                    full_response + "▌"
                )

            message_placeholder.markdown(full_response)

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            st.error(f"Erreur Ollama : {e}")
