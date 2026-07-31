import streamlit as st
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

st.set_page_config(page_title="Zeus AI", layout="wide")

st.title("Zeus, our Free AI on the Web")
st.write("First App")
st.header("Welcome!")
st.subheader("AI Level 2")

count = 0
if st.button("Click me"):
    count += 1
st.write("count is", count)

with st.sidebar:
    st.header("Settings")
    with st.form("Settings"):
        name = st.text_input("What is your name?")
        creativity = st.slider("Creativity", 0.0, 1.0, 0.5)
        sources = st.multiselect("Select a few options", ["My first app", "My second app", "My third app"])
        saved = st.form_submit_button("Save")
    if (saved):
        st.write(f"Saved sources: {sources} and creativity: {creativity}")
left, right = st.columns(2)
left.write(f"Sources: {len(sources)}")
right.write(f"Creativity: {creativity} ")

prompt = st.chat_input("Ask me something here...")
if prompt:
    with st.chat_message("User"):
        st.write(f"{prompt}")
    with st.chat_message("Chat Bot"):
        load_dotenv()
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ.get("AI_TOKEN") or st.secrets("AI_TOKEN"),
        )
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        st.write(r.choices[0].message.content)
