import os
import openai
import streamlit as st
from dotenv import load_dotenv


# --- LOAD ENVIRONMENT VARIABLES --- # 
load_dotenv()


# --- LOAD API KEYS --- # 

# Load OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load PINECONE_API_KEY
api_key_pinecone = os.getenv("PINECONE_API_KEY")

# Set up PINECONE_ENVIRONMENT
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")

# Set up PINECONE_ENDPOINT
pinecone_endpoint = os.getenv("PINECONE_ENDPOINT")



# --- RETRIEVAL AUGMENTED GENERATION --- # 

# Create embeddings from user query & MicodeGPT reponses 
def get_embeddings_openai(text):
    try:
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        response = response['data']
        return [x["embedding"] for x in response]
    except Exception as e:
        print(f"Error in get_embeddings_openai: {e}")
        raise

# Semantic search in PINECONE Database
def semantic_search(query, index, **kwargs):
    try:
        xq = get_embeddings_openai(query)

        xr = index.query(vector=xq[0], top_k=kwargs.get('top_k', 3), include_metadata=kwargs.get('include_metadata', True))

        if xr.error:
            print(f"Invalid response: {xr}")
            raise Exception(f"Query failed: {xr.error}")

        titles = [r["metadata"]["video_title"] for r in xr["matches"]]
        transcripts = [r["metadata"]["text"] for r in xr["matches"]]
        sources = [r["metadata"]["video_url"] for r in xr["matches"]] # Add sources
        return list(zip(titles, transcripts, sources))
    
    

    except Exception as e:
        print(f"Error in semantic_search: {e}")
        raise
