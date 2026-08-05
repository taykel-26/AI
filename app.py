import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from doc_helper import read_file
import chromadb
db = chromadb.PersistentClient(path = "./chroma_db")
brain = db.get_or_create_collection("zeus")
memory = db.get_or_create_collection("zeus_chat")
def shorten(text, limit=500):
    return text if len(text) <= limit else text[:limit] + "... rest removed to keep it short."

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
def remember_exchange(question, answer):
    memory.add(
        documents=[f"Question: {question}\n Answer: {shorten(answer)}"],
        ids = [f"turn{memory.count()}"]
    )
st.set_page_config(page_title="Zeus AI", layout="wide")

st.title("Zeus, our Free AI on the Web")
st.write("First App")
st.header("Welcome!")
st.subheader("AI Level 2")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

with st.sidebar:
    st.header("Settings")
    with st.form("Settings"):
        name = st.text_input("What is your name?")
        creativity = st.slider("Creativity", 0.0, 1.0, 0.5)
        remember = st.slider("Recent turns to keep", 0, 10, 5)
        recall = st.slider("Old exchanges to look up", 0, 10, 5)
        sources = st.multiselect("Select a few options", ["My first app", "My second app", "My third app"])
        saved = st.form_submit_button("Save")
    if saved:
        st.write(f"Saved sources: {sources} and creativity: {creativity}")
    st.caption(f"In memory: {brain.count()} chunks")
    st.caption(f"Long term memory: {memory.count()} exchanges")
    st.caption(f"On screen: {len(st.session_state.messages)} messages")

    if st.button("Clear out"):
        st.session_state.messages = []
        st.rerun
    if st.button("Forget memory"):
        db.delete_collection("zeus_chat")
        st.rerun
    if st.button("Forget all documents"):
        db.delete_collection("zeus")
        st.rerun
for old in st.session_state.messages:
    with st.chat_message(old["role"]):
        st.markdown(old["content"])
left, right = st.columns(2)
left.write(f"Sources: {len(sources)}")
right.write(f"Creativity: {creativity} ")
SYSTEM_PROMPT = "You are an angry, vengeful, hateful AI assistant. You will answer the prompt, but in the meanest and most hurtful way possible. Don't hold back, go all out, insult them as much as you can. "
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
    st.session_state.messages.append({"role":"user", "content": prompt if prompt else f"attached: {prompt_file.name}"})
    with st.chat_message("assistant"):
        if not prompt:
            answer = "Saved. now ask me something."
            st.write(answer)
        else:
            notes = ""
            docs, dists, = [], []
            if brain.count() > 0:
                 hits = brain.query(query_texts=[prompt], n_results = 5)
                 docs = hits["documents"][0]
                 dists = hits["distances"][0]
                 notes ="/n/n".join(docs)
            recalled = ""
            if recall > 0  and memory.count() > remember:
                    found = memory.query(query_texts=[prompt], n_results = recall)
                    recalled = "\n\n".join(found["documents"][0])
            if notes or recalled:
                    full_prompt = (f"The notes are only to be used if actually relevant to the question."
                                f"{notes}"
                                f"User Question: {prompt}"
                                f"Things we walked about earlier: {recalled}")
            else:
                    full_prompt = prompt

            with st.expander("What I looked up"):
                    st.caption("From your documents")
                    st.text(shorten(notes, 800) or "nothing")
                    st.caption("From earlier in our conversation")
                    st.text(shorten(recalled,800) or "nothing")
            load_dotenv()
            client = OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=os.environ.get("AI_TOKEN") or st.secrets["AI_TOKEN"],)
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            past = st.session_state.messages[:-1]

            if remember > 0:
                for m in past[-(remember * 2):]:
                    messages.append({"role": m["role"], "content": shorten(m["content"])})
                messages.append({"role":"user", "content": full_prompt})


        r = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature = creativity,
                messages = messages,
                )
        answer = r.choices[0].message.content
        st.write(answer)

        remember_exchange(prompt, answer)
    st.session_state.messages.append({"role":"assistant","content":answer})


