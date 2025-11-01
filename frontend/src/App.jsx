import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    setMessages([...messages, userMsg]);
    setInput("");

    const res = await axios.post("http://127.0.0.1:8000/chat", { message: input });
    const botMsg = { role: "assistant", content: res.data.reply };
    setMessages((msgs) => [...msgs, botMsg]);
  };

  return (
    <div className="chat-container">
      <h1>🧭 Milo — Insurance Chatbot</h1>
      <div className="chat-box">
        {messages.map((m, i) => (
          <p key={i} className={m.role}>
            <b>{m.role === "user" ? "You" : "Milo"}:</b> {m.content}
          </p>
        ))}
      </div>
      <div className="input-box">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me about travel insurance..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;
