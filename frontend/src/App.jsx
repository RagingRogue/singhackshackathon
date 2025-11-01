import { useState, useEffect, useRef } from "react";
import {
  Input,
  Button,
  List,
  Avatar,
  Typography,
  Layout,
  theme,
} from "antd";
import {
  SendOutlined,
  UserOutlined,
  RobotOutlined,
} from "@ant-design/icons";
import axios from "axios";

const { Content, Header, Footer } = Layout;
const { Text } = Typography;

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/chat", {
        message: input,
      });

      const botMsg = { role: "assistant", content: res.data.reply };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "❌ Server error. Please try again later." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout
      style={{
        minHeight: "100vh",
        background: theme.defaultAlgorithm.colorBgContainer,
      }}
    >
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
          {/* Scrollable Chat Box */}
          <div
            style={{
              height: "65vh",
              overflowY: "auto",
              padding: "16px",
              background: "#fff",
              border: "1px solid #f0f0f0",
              borderRadius: 10,
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
                    transition: "all 0.2s ease-in-out",
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
                      <Text strong>
                        {msg.role === "user" ? "You" : "Milo"}
                      </Text>
                    }
                    description={
                      <span style={{ whiteSpace: "pre-wrap" }}>
                        {msg.content}
                      </span>
                    }
                  />
                </List.Item>
              )}
            />
            {/* Invisible marker for scroll-to-bottom */}
            <div ref={chatEndRef} />
          </div>

          {/* Input Bar */}
          <div
            style={{
              display: "flex",
              marginTop: 16,
              gap: 8,
            }}
          >
            <Input
              placeholder="Ask me about travel insurance..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onPressEnter={sendMessage}
              disabled={loading}
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
