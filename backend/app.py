# Backend (Python) - app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import praw
import os
from dotenv import load_dotenv
import chromadb
from langchain_together import TogetherEmbeddings, ChatTogether
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

# Initialize Together AI Embeddings
embeddings_model = TogetherEmbeddings(
    model="togethercomputer/m2-bert-80M-8k-retrieval",
)

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Initialize ChromaDB client
chroma_client = chromadb.Client()

# Create a collection in ChromaDB
collection = chroma_client.create_collection(name="subreddit_embeddings")

# Initialize ChatTogether with Llama model
llm = ChatTogether(
    api_key=os.getenv("TOGETHER_API_KEY"),
    temperature=0.0,
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
)

@app.route('/connect', methods=['POST'])
def connect_subreddit():
    print(f"Reached connecting point with {request.json}")
    data = request.json
    subreddit_name = data['subreddit']
    
    try:
        # Get subreddit content
        subreddit = reddit.subreddit(subreddit_name)
        posts = []

        for post in subreddit.hot(limit=10):
            post_data = {
                'title': post.title,
                'content': post.selftext,
                'comments': [comment.body for comment in post.comments[:20]]
            }
            posts.append(post_data)

        # Prepare text for vectorization
        all_text = [post['content'] + "\n" + "\n".join(post['comments']) for post in posts]

        # Split text into chunks
        # split_texts = []
        # for text in all_text:
        #     splits = text_splitter.split_documents([{"text": text}])
        #     split_texts.extend([split['text'] for split in splits])

        # Create embeddings using Together AI
        embeddings = embeddings_model.embed_documents(all_text)

        # Add embeddings to ChromaDB
        for idx, (text, embedding) in enumerate(zip(all_text, embeddings)):
            collection.add(
                documents=[text],
                metadatas=[{"text": str(idx)}],
                ids=[str(idx)]
            )

        return jsonify({
            'status': 'success',
            'message': f'Successfully connected to r/{subreddit_name}'
        })

    except Exception as e:
        print(f"Error connecting to subreddit: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data['message']
    
    if collection is None:
        return jsonify({
            'status': 'error',
            'message': 'Please connect to a subreddit first'
        }), 400

    try:
        # Query ChromaDB for relevant documents
        results = collection.query(
            query_texts=[query],
            n_results=1
        )

        # Extract the document text from the query results
        document_text = results["documents"][0][0]

        # Send the document text to the Llama LLM
        response = llm(document_text)
        print(response)
        # # Format response
        # llm_response = response.choices[0].message.content

        return jsonify({
            'status': 'success',
            'message': document_text
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)