# debugger.py
from app import connect_subreddit, chat

def test_connect_subreddit():
    result = connect_subreddit("algotrading")
    print("Connect Subreddit Result:")
    print(result)

def test_chat():
    result = chat("low latency")
    print("Chat Result:")
    print(result)

if __name__ == "__main__":
    test_connect_subreddit()
    test_chat()