import os
import openai
import streamlit as st
from dotenv import load_dotenv
from render import *
from utils import *
import prompts
from pinecone import Pinecone


# --- LOAD ENVIRONMENT VARIABLES --- # 
load_dotenv()


# --- SET PAGE CONFIG --- # 
st.set_page_config(page_title="MicodeGPT", page_icon=":computer:")


# --- LOAD CSS STYLE --- # 
with open('./styles/style.css') as f:
    css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


# --- LOAD OPENAI API KEY --- # 
openai.api_key = os.getenv("OPENAI_API_KEY")


# --- LOAD PINECONE API KEY --- # 
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


# --- LOAD PINECONE INDEX --- # 
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))




### ------ ////// MICODE GPT MAIN APP \\\\\\ ------ #### 

# --- PAGE LAYOUT --- # 
# Split Page into 2 columns
col1, col2 = st.columns([1,3])

# --- LEFT COLUMN --- # 
# MicodeGPT Avatar
with col1:
    st.write("")
    col1.image(
            "assets/Micode.png",
            # Manually Adjust the width of the image as per requirement
             )

# --- RIGHT COLUMN --- #  
# Name of the GPT
with col2:
    col1a, col2a = st.columns([0.01,10000])    
    col2a.header("💻 MicodeGPT")

# MicodeGPT - Descriptive introduction for user 
with col2:
    col1, col2 = st.columns([1,100])
    col2.write("Bonjour, je suis MicodeGPT, une IA entraînée sur les vidéos de ma chaîne YouTube *\"Underscore_\"* où je débrief les histoires les plus folles de l'IT. Posez-moi vos questions, et je ferai de mon mieux pour y répondre en vous fournissant les liens de vidéos pertinentes pour approfondir le sujet.")


# --- CHAT HISTORY & MESSAGE MANAGEMENT LOGIC --- #  
# Define chat history storage
if "history" not in st.session_state:
    st.session_state.history = []

# Construct messages from chat history
def construct_messages(history):
    messages = [{"role": "system", "content": prompts.system_message}]
    
    for entry in history:
        role = "user" if entry["is_user"] else "assistant"
        messages.append({"role": role, "content": entry["message"]})
    
    return messages

# Generate response to user prompt
def generate_response():
    st.session_state.history.append({
        "message": st.session_state.prompt,
        "is_user": True,
    })
    

    print(f"Query: {st.session_state.prompt}")
    unique_sources = set()  # Use a set to store unique source titles

    # Perform semantic search and format results
    search_results = semantic_search(st.session_state.prompt, index, top_k=3)

    print(f"Results: {search_results}")

    context = ""
    for i, (title, transcript, source) in enumerate(search_results):
        context += f"Snippet from: {title}\n {transcript}\n\n"
        unique_sources.add(source)  # Add unique source urls to the set

    # Generate human prompt template and convert to API message format
    query_with_context = prompts.human_template.format(query=st.session_state.prompt, context=context)

    # Convert chat history to a list of messages
    messages = construct_messages(st.session_state.history)
    messages.append({"role": "user", "content": query_with_context})

    # Run the LLMChain
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    print(messages)

    # Parse response
    bot_response = response["choices"][0]["message"]["content"]

    # Add source titles to the bot response
    sources_text = "Source(s): " + ", <br>".join(unique_sources)
    bot_response_with_sources = bot_response + "\n\n <br>" + sources_text

    st.session_state.history.append({
        "message": bot_response_with_sources,
        "is_user": False
    })

    st.session_state.prompt = ''


# Display chat history
for message in st.session_state.history:
    if message["is_user"]:
        st.write(user_msg_container_html_template.replace("$MSG", message["message"]), unsafe_allow_html=True)
    else:
        st.write(bot_msg_container_html_template.replace("$MSG", message["message"]), unsafe_allow_html=True)

# User input prompt
# st.write(" ")
user_prompt = st.text_input(" ",
                            key="prompt",
                            placeholder="Écrivez votre message...",
                            on_change=generate_response,
                            )


# COPYRIGHT
st.markdown("<div style='text-align: right; color: #83858C; font-size:14px;'>&copy; 2024 Copyright <a href='https://www.linkedin.com/in/mathieubekkaye'>Mathieu Bekkaye</a> - All rights reserved.</div>", unsafe_allow_html=True)
# st.markdown("<div style='text-align: right; color: #83858C; font-size:14px;'>&copy; 2024 Copyright <a href='https://mathieubk-personalwebsite.streamlit.app'>Mathieu Bekkaye</a> - All rights reserved.</div>", unsafe_allow_html=True)




