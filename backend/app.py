# Backend (Python) - app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import praw
import pandas as pd
from together import Together
from dotenv import load_dotenv
load_dotenv()
import os
from langchain_together import ChatTogether

app = Flask(__name__)
CORS(app)

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

# Initialize Together AI client
llm = ChatTogether(
    api_key=os.getenv("together_API_Key"),
    temperature=0.0,
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
)


# Initialize vector store
vector_store = None

@app.route('/connect', methods=['POST'])
def connect_subreddit():
    print(f"Reached connecting point with {request.json}")
    data = request.json
    subreddit_name = data['subreddit']
    
    try:
        # Get subreddit content
        subreddit = reddit.subreddit(subreddit_name)
        posts = []
        
        # Collect hot posts and their comments
        for post in subreddit.hot(limit=50):
            post_data = {
                'title': post.title,
                'content': post.selftext,
                'comments': []
            }
            
            post.comments.replace_more(limit=0)
            for comment in post.comments[:20]:
                post_data['comments'].append(comment.body)
            
            posts.append(post_data)
        
        # Prepare text for vectorization
        all_text = []
        for post in posts:
            all_text.append(post['title'])
            all_text.append(post['content'])
            all_text.extend(post['comments'])
        
        # Create embeddings using Together AI
        # embeddings = []
        # for text in all_text:
        #     completion = client.chat.completions.create(
        #         model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        #         messages=[{"role": "user", "content": text}]
        #     )
        #     embeddings.append(completion['choices'][0]['message']['content'])
        
        # # Store embeddings in a suitable data structure
        # global vector_store
        # vector_store = embeddings
        
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
    
    if vector_store is None:
        return jsonify({
            'status': 'error',
            'message': 'Please connect to a subreddit first'
        }), 400
    
    try:
        # Search similar content in vector store
        # Implement a similarity search using the embeddings
        # This is a placeholder for the actual similarity search logic
        results = vector_store[:3]  # Replace with actual search logic
        
        # Format response
        response = "Based on the subreddit content:\n\n"
        for doc in results:
            response += f"- {doc}\n\n"
        
        return jsonify({
            'status': 'success',
            'message': response
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)