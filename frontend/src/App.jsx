import { useState, useEffect, useRef } from "react";
import {
  Input,
  Button,
  List,
  Avatar,
  Typography,
  Layout,
  message as AntMessage,
} from "antd";
import {
  SendOutlined,
  UserOutlined,
  RobotOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import axios from "axios";

const { Content, Header, Footer } = Layout;
const { Text } = Typography;

const GREETING_MESSAGE = {
  role: "assistant",
  content:
    "👋 Hey there! I’m **Milo**, your friendly travel insurance guide. Before we get started, tell me a bit about your trip ✈️ — where are you headed, how long will you be staying, and what’s the purpose of your travel?",
};

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([GREETING_MESSAGE]);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

useEffect(() => {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("payment") === "success") {
    axios.get("http://127.0.0.1:8000/api/payment-status").then((res) => {
      if (res.data.status === "success") {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "✅ Payment successful! Your policy has been issued and sent to your email."
          }
        ]);
      }
    });
  }
}, []);

 const sendMessage = async () => {
  if (!input.trim()) return;

  const userMsg = { role: "user", content: input };
  setMessages((prev) => [...prev, userMsg]);
  setInput("");
  setLoading(true);

  try {
    // ✅ If user explicitly wants to buy → directly give them Stripe link
    if (input.toLowerCase().includes("buy")) {
      const paymentUrl = "https://buy.stripe.com/test_28E4gB3CTcGj8uC53ffUQ00"; // <-- your Stripe Checkout link
      const botMsg = {
        role: "assistant",
        content: `🛒 Sure! You can purchase your travel insurance here:\n\n**👉 [Click to Pay](${paymentUrl})**\n\nOnce payment is completed, I’ll send your confirmation! ✅`,
      };
      setMessages((prev) => [...prev, botMsg]);
    } else {
      // ✅ Normal chatbot response
      const res = await axios.post("http://127.0.0.1:8000/chat", {
        message: input,
        user_id: "demo_user",
      });
      const botMsg = { role: "assistant", content: res.data.reply };
      setMessages((prev) => [...prev, botMsg]);
    }
  } catch (err) {
    console.error(err);
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content:
          "⚠️ An error occurred while processing your request. Please try again.",
      },
    ]);
  } finally {
    setLoading(false);
  }
};

  useEffect(() => {
  // Load saved messages on startup
  const savedMessages = localStorage.getItem("chatMessages");
  if (savedMessages) {
    setMessages(JSON.parse(savedMessages));
  }
}, []);

useEffect(() => {
  // Save messages on every update
  localStorage.setItem("chatMessages", JSON.stringify(messages));
}, [messages]);


  useEffect(() => {
  const params = new URLSearchParams(window.location.search);
  if (params.get("payment") === "success") {
    setMessages(prev => [
      ...prev,
      {
        role: "assistant",
        content:
          "✅ Payment successful! Your policy has been issued and a confirmation email has been sent."
      }
    ]);
  }
}, []);


  const resetConversation = async () => {
    try {
      await axios.post("http://127.0.0.1:8000/reset");
      setMessages([GREETING_MESSAGE]);
      AntMessage.success("Conversation reset!");
    } catch (err) {
      console.error(err);
      AntMessage.error("Failed to reset conversation.");
    }
  };

  return (
    <Layout style={{ minHeight: "100vh", background: "#f0f2f5" }}>
      <Header
        style={{
          color: "white",
          fontSize: "1.3rem",
          fontWeight: 600,
          background: "#1677ff",
        }}
      >
        🧭 Milo — Insurance Chatbot
      </Header>

      <Content
        style={{
          padding: "24px",
          display: "flex",
          justifyContent: "center",
        }}
      >
        <div style={{ width: "100%", maxWidth: 700 }}>
          <div
            style={{
              height: "65vh",
              overflowY: "auto",
              padding: "16px",
              background: "#fff",
              border: "1px solid #d9d9d9",
              borderRadius: 10,
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
            }}
          >
            <List
              dataSource={messages}
              renderItem={(msg) => (
                <List.Item
                  className="fade-in"
                  style={{
                    background:
                      msg.role === "user" ? "#e6f7ff" : "#fafafa",
                    borderRadius: 8,
                    marginBottom: 8,
                    color: "#000", // 🔥 darker text
                  }}
                >
                  <List.Item.Meta
                    avatar={
                      msg.role === "user" ? (
                        <Avatar
                          icon={<UserOutlined />}
                          style={{ backgroundColor: "#1890ff" }}
                        />
                      ) : (
                        <Avatar
                          icon={<RobotOutlined />}
                          style={{ backgroundColor: "#722ed1" }}
                        />
                      )
                    }
                    title={
                      <Text strong style={{ color: "#000" }}>
                        {msg.role === "user" ? "You" : "Milo"}
                      </Text>
                    }
                    description={
                      <div
                        style={{
                          color: "#333", // darker readable text
                          lineHeight: 1.6,
                        }}
                      >
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
            <div ref={chatEndRef} />
          </div>

          <div
            style={{
              display: "flex",
              marginTop: 16,
              gap: 8,
              alignItems: "center",
            }}
          >
            <Button
              icon={<ReloadOutlined />}
              onClick={resetConversation}
              shape="circle"
              danger
              type="default"
              title="Reset conversation"
            />

            <Input
              placeholder="Ask me about travel insurance..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onPressEnter={sendMessage}
              disabled={loading}
              style={{ fontSize: "1rem" }}
            />

            <Button
              type="primary"
              icon={<SendOutlined />}
              loading={loading}
              onClick={sendMessage}
            >
              Send
            </Button>
          </div>
        </div>
      </Content>

      <Footer style={{ textAlign: "center" }}>
        <Text type="secondary">
          Powered by Groq GPT-OSS-20B | FastAPI Backend
        </Text>
      </Footer>
    </Layout>
  );
}

export default App;
