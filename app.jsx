function App() {
  const [messages, setMessages] = React.useState([]);
  const [input, setInput] = React.useState("");

  async function sendMessage() {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");

    const res = await fetch("http://localhost:3000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input })
    });

    const data = await res.json();
    const botMsg = { role: "bot", text: data.answer };

    setMessages(prev => [...prev, botMsg]);
  }

  function handleKey(e) {
    if (e.key === "Enter") sendMessage();
  }

  return (
    <div className="chat-container">
      <div className="chat-header">Jarvis</div>

      <div className="chat-body">
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            {m.text}
          </div>
        ))}
      </div>

      <div className="chat-input">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Message Jarvis..."
        />
        <button onClick={sendMessage}>➤</button>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
