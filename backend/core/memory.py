chat_sessions = {}

def get_session(user_id: str):
    if user_id not in chat_sessions:
        chat_sessions[user_id] = [
            {"role": "system", "content": "You are Milo, a friendly and witty travel insurance assistant who remembers past context."}
        ]
    return chat_sessions[user_id]

def clear_sessions():
    chat_sessions.clear()
