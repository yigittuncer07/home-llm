import React, { useState } from 'react';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newMessages = [...messages, { text: input, sender: 'user' }];
    setMessages(newMessages);
    setInput('');

    try {
      const response = await fetch('http://localhost:80/api/items/2');
      
      // Attempt to parse as JSON first, fallback to text
      const isJson = response.headers.get('content-type')?.includes('application/json');
      const data = isJson ? await response.json() : await response.text();
      const botReply = typeof data === 'object' ? JSON.stringify(data) : data;

      setMessages([...newMessages, { text: botReply, sender: 'bot' }]);
    } catch (error) {
      setMessages([...newMessages, { text: 'Error connecting to backend.', sender: 'bot' }]);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.chatBox}>
        {messages.map((msg, index) => (
          <div key={index} style={msg.sender === 'user' ? styles.userMsg : styles.botMsg}>
            {msg.text}
          </div>
        ))}
      </div>
      <form onSubmit={handleSend} style={styles.form}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Send a message to ping /status..."
        />
        <button type="submit" style={styles.button}>Send</button>
      </form>
    </div>
  );
}

const styles = {
  container: { width: '400px', margin: '40px auto', border: '1px solid #ddd', borderRadius: '8px', fontFamily: 'sans-serif' },
  chatBox: { height: '400px', overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px', backgroundColor: '#f8f9fa' },
  userMsg: { alignSelf: 'flex-end', backgroundColor: '#007bff', color: 'white', padding: '10px 14px', borderRadius: '16px 16px 0 16px', maxWidth: '75%', wordWrap: 'break-word' },
  botMsg: { alignSelf: 'flex-start', backgroundColor: '#e9ecef', color: '#212529', padding: '10px 14px', borderRadius: '16px 16px 16px 0', maxWidth: '75%', wordWrap: 'break-word' },
  form: { display: 'flex', borderTop: '1px solid #ddd' },
  input: { flex: 1, padding: '12px', border: 'none', borderBottomLeftRadius: '8px', outline: 'none' },
  button: { padding: '0 20px', backgroundColor: '#28a745', color: 'white', border: 'none', borderBottomRightRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }
};