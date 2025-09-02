import { useState, useRef, useEffect } from "react";
import "../static/style.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface ChatMessage {
  role: string;
  content: string;
}

interface ClassificationResult {
  categoria?: string;
  resposta?: string;
}

function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [chatActive, setChatActive] = useState(false);
  const [chatMessage, setChatMessage] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const chatMessagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll para o final das mensagens do chat
  const scrollToBottom = () => {
    chatMessagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, chatLoading]);

  const handleSubmit = async () => {
    if (!text.trim() && !file) {
      alert("Digite um texto ou selecione um arquivo.");
      return;
    }

    setLoading(true);
    setResult(null);
    
    try {
      let response;
      if (file) {
        const formData = new FormData();
        formData.append("file", file);
        response = await fetch(`${API_URL}/upload_file`, {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch(`${API_URL}/process_text`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        });
      }

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(errText || "Erro na requisição");
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      alert("Erro: " + (err.message || err));
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setText(""); // Limpa o texto quando um arquivo é selecionado
    }
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    if (e.target.value) setFile(null); // Limpa o arquivo quando texto é digitado
  };

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;

    setChatLoading(true);
    const userMessage = chatMessage;
    setChatMessage("");

    // Adiciona mensagem do usuário ao histórico
    const newHistory = [...chatHistory, { role: "user", content: userMessage }];
    setChatHistory(newHistory);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: userMessage, 
          history: newHistory 
        }),
      });

      if (!response.ok) {
        throw new Error("Erro na requisição do chat");
      }

      const data = await response.json();
      
      // Atualiza o histórico com a resposta do assistente
      setChatHistory(data.history || newHistory);
    } catch (err: any) {
      alert("Erro no chat: " + (err.message || err));
      // Reverte a mensagem do usuário em caso de erro
      setChatHistory(chatHistory);
      setChatMessage(userMessage);
    } finally {
      setChatLoading(false);
    }
  };

  const clearChat = () => {
    setChatHistory([]);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>📧 Classificação de Emails - AutoU</h1>
      </header>
      <div></div>
      {chatActive && (
        <div className="chat-container">
          <div className="chat-header">
            <h3>Assistente Virtual</h3>
            <p>Posso ajudar com dúvidas sobre classificação de emails</p>
            <button className="clear-chat" onClick={clearChat}>Limpar</button>
          </div>
          
          <div className="chat-messages">
            {chatHistory.length === 0 ? (
              <div className="chat-welcome">
                <p>👋 Olá! Sou o assistente da AutoU. Como posso ajudar você hoje?</p>
                <p>Posso explicar sobre classificação de emails, sugerir respostas ou tirar outras dúvidas.</p>
              </div>
            ) : (
              chatHistory.map((msg, index) => (
                <div key={index} className={`chat-message ${msg.role}`}>
                  <div className="message-content">
                    {msg.role === 'user' ? '👤 ' : '🤖 '}
                    {msg.content}
                  </div>
                </div>
              ))
            )}
            {chatLoading && (
              <div className="chat-message assistant">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={chatMessagesEndRef} />
          </div>
          
          <form onSubmit={handleChatSubmit} className="chat-input">
            <input
              type="text"
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              placeholder="Digite sua pergunta..."
              disabled={chatLoading}
            />
            <button type="submit" disabled={chatLoading || !chatMessage.trim()}>
              {chatLoading ? "..." : "Enviar"}
            </button>
          </form>
        </div>
      )}
      
      <div className="main-content">
        <div className="input-section">
          <h2>Analisar Email</h2>
          <textarea
            placeholder="Cole o conteúdo do email aqui..."
            value={text}
            onChange={handleTextChange}
            rows={6}
          />
          
          <div className="file-upload">
            <p>Ou selecione um arquivo:</p>
            <div className="file-input-container">
              <input
                type="file"
                accept=".txt,.pdf"
                onChange={handleFileChange}
                id="file-input"
              />
              <label htmlFor="file-input" className="file-input-label">
                📎 Escolher arquivo
              </label>
            </div>
            {file && <p className="file-name">Arquivo selecionado: {file.name}</p>}
          </div>
          
          <button onClick={handleSubmit} disabled={loading} className="submit-btn">
            {loading ? "⏳ Classificando..." : "📤 Enviar para análise"}
          </button>
        </div>

        {result && (
          <div className="result-section">
            <h2>Resultado da Análise</h2>
            <div className={`category ${result.categoria?.toLowerCase()}`}>
              <span className="category-icon">
                {result.categoria === 'Produtivo' ? '✅' : 'ℹ️'}
              </span>
              <div className="category-info">
                <strong>Categoria:</strong> {result.categoria}
              </div>
            </div>
            <div className="suggestion">
              <h3>Resposta sugerida:</h3>
              <div className="suggestion-content">
                <p>{result.resposta}</p>
              </div>
              <button 
                className="copy-btn"
                onClick={() => {
                  navigator.clipboard.writeText(result.resposta || '');
                  alert('Resposta copiada para a área de transferência!');
                }}
              >
                📋 Copiar resposta
              </button>
            </div>
          </div>
        )}
          
      </div>
        <div className="botão">
           <button 
        className="chat-toggle"
        onClick={() => setChatActive(!chatActive)}
      >
        {chatActive ? "✕ Fechar Assistente" : "💬 Abrir Assistente"}
      </button>
        </div>

    <footer className="app-footer">
      </footer>
    </div>
  );
}

export default App;