from PIL import Image
import io
import streamlit as st
import google.generativeai as genai
import google.ai.generativelanguage as glm

with st.sidebar:
    st.title("Gemini API")
    
    api_key = st.text_input("API key")
    if api_key:
        genai.configure(api_key=api_key)
    else:
        if "api_key" in st.secrets:
            genai.configure(api_key=st.secrets["api_key"])
        else:
            st.error("Missing API key.")
    
    select_model = st.selectbox("Select Model", ["gemini-pro", "gemini-pro-vision"])
    if select_model == "gemini-pro-vision":
        uploaded_image = st.file_uploader(
            "upload image",
            label_visibility="collapsed",
            accept_multiple_files=False,
            type=["png", "jpg"],
        )
        st.caption(
            "Note: The vision model gemini-pro-vision is not optimized for multi-turn chat."
        )
        if uploaded_image:
            image_bytes = uploaded_image.read()

def get_response(messages, model="gemini-pro"):
    model = genai.GenerativeModel(model)
    res = model.generate_content(messages, stream=True,
                                safety_settings={'HARASSMENT':'block_none'})
    return res

if "messages" not in st.session_state:
    st.session_state["messages"] = []
messages = st.session_state["messages"]

# The vision model gemini-pro-vision is not optimized for multi-turn chat.
if messages and select_model != "gemini-pro-vision":
    for item in messages:
        role, parts = item.values()
        if role == "user":
            st.chat_message("user").markdown(parts[0])
        elif role == "model":
            st.chat_message("assistant").markdown(parts[0])

chat_message = st.chat_input("Say something")

if chat_message:
    st.chat_message("user").markdown(chat_message)
    res_area = st.chat_message("assistant").empty()

    if select_model == "gemini-pro-vision":
        if "image_bytes" in globals():
            vision_message =  [chat_message, Image.open(io.BytesIO(image_bytes))]
            res = get_response(vision_message, model="gemini-pro-vision")
        else:
            vision_message = [{"role": "user", "parts": [chat_message]}]
            st.warning("Since there is no uploaded image, the result is generated by the default gemini-pro model.")
            res = get_response(vision_message)
    else:
        messages.append(
            {"role": "user", "parts":  [chat_message]},
        )
        res = get_response(messages)

    res_text = ""
    for chunk in res:
        res_text += chunk.text
        res_area.markdown(res_text)

    if select_model != "gemini-pro-vision":
        messages.append({"role": "model", "parts": [res_text]})
