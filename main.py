from idlelib.window import ListedToplevel

import streamlit as st
st.title("Zeus, our Free AI on the Web")

st.write("First App")
st.header("Welcome!")
st.subheader("AI Level 2")

count = 0
if st.button("Click me"):
    count += 1
st.write("count is", count)
x = "a" and "e" and "i" and "o" and "u"
name = st.text_input("What is your name?")
if st.button("Submit"):
    st.write(f"Hello {name}! Welcome to AI level 2.")
    st.write(f"Hey {name}! Your name has {len(name)} characters.")

with st.sidebar:
    st.header("Settings")
    with st.form("Settings"):
        creativity = st.slider("Creativity", 0.0, 1.0, 0.5)
        sources = st.multiselect("Select a few options", ["My first app", "My second app", "My third app"])
        saved = st.form_submit_button("Save")
    if (saved):
        st.write(f"Saved sources: {sources} and creativity: {creativity}")
left, right = st.columns(2)
left.write(f"Sources: {len(sources)}")
right.write(f"Creativity: {creativity} ")

with st.chat_message("User"):
    st.write(f"Hello, I am {name}! Welcome to AI level 2.")
with st.chat_message("Chat Bot"):
    st.write(f"Hello, {name}! I am Zeus, welcome to AI level 2.")

prompt = st.chat_input("Ask me something here...")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)