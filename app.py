import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from doc_helper import read_file
import chromadb

db = chromadb.PersistentClient(path = "./chroma_db")
brain = db.get_or_create_collection("zeus")
def chunk_by_sentence(text, max_size = 400):
    sentences = text.split(". ")
    chunks, current = [],""
    for sentence in sentences:
        if len(current) + len(sentence) < max_size:
            current += sentence + ". "
        else:
            if current.strip():
                chunks.append(current.strip())
            current = sentence + ". "
    if current.strip():
        chunks.append(current.strip())
    return chunks

def store_document(file):
    raw = read_file(file)
    chunks = chunk_by_sentence(text)
    prefix = file.name.replace(" ", "_")
    brain.add(
        documents=chunks,
        ids = [f"{prefix}_chunk{i}" for i in range(len(chunks))],
    )
    return len(raw), len(text), len(chunks)

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
    if saved:
        st.write(f"Saved sources: {sources} and creativity: {creativity}")
    st.caption(f"In memory: {brain.count()} chunks")
left, right = st.columns(2)
left.write(f"Sources: {len(sources)}")
right.write(f"Creativity: {creativity} ")
SYSTEM_PROMPT = "You are an good help assistant. "
user_input = st.chat_input(
    "Ask me something here...",
    accept_file=True,
    file_type=["pdf", "txt"],)
if user_input:
    prompt = user_input.text
    prompt_file = None
    if user_input.files:
        prompt_file = user_input.files[0]
    with st.chat_message("User"):
        if prompt_file:
            text = read_file(prompt_file)
            raw_len, clean_len, n_chunks = store_document(prompt_file)
            st.write(f"**{prompt_file.name}**")
            st.caption(f"{raw_len} characters "
                       f"stored as {n_chunks} chunks")
        if prompt:
            st.write(f"{prompt}")
    with st.chat_message("assistant"):
        notes = ""
        if brain.count() > 0:
            hits = brain.query(query_texts=[prompt], n_results = 5)
            notes ="/n/n".join(hits["documents"][0])
            if notes:
                full_prompt = (f"The notes are only to be used if actually relevant to the question."
                               f"{notes}"
                               f"User Question: {prompt}")
            else:
                full_prompt = prompt
        load_dotenv()
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ.get("AI_TOKEN") or st.secrets["AI_TOKEN"],
        )
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=creativity,
            messages=[{"role": "user", "content": full_prompt}],
        )
        st.write(r.choices[0].message.content)

