import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './PolicyChatbot.css'

const API_BASE = 'https://policy-drift-detection-1.onrender.com'

function PolicyChatbot({ policyId }) {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const suggestedQuestions = [
    "Why was District X flagged?",
    "Which policy rules are most frequently violated?",
    "Explain this constraint simply",
    "Show trends after policy updates"
  ]

  useEffect(() => {
    if (policyId) {
      startSession()
    }
  }, [policyId])

  useEffect(() => {
    if (sessionId) {
      loadMessages()
    }
  }, [sessionId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const startSession = async () => {
    try {
      const response = await axios.post(`${API_BASE}/chat/start`, null, {
        params: { policy_id: policyId }
      })
      setSessionId(response.data.session_id)
    } catch (err) {
      console.error('Failed to start chat session:', err)
    }
  }

  const loadMessages = async () => {
    if (!sessionId) return
    try {
      const response = await axios.get(`${API_BASE}/chat/sessions/${sessionId}/messages`)
      setMessages(response.data.messages || [])
    } catch (err) {
      console.error('Failed to load messages:', err)
    }
  }

  const sendMessage = async (messageText = null) => {
    const text = messageText || input.trim()
    if (!text || !sessionId || loading) return

    try {
      setLoading(true)
      const userMessage = {
        role: 'user',
        content: text,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, userMessage])
      setInput('')

      const response = await axios.post(`${API_BASE}/chat/message`, null, {
        params: {
          session_id: sessionId,
          message: text
        }
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      console.error('Failed to send message:', err)
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    sendMessage()
  }

  const handleSuggestedQuestion = (question) => {
    setInput(question)
    setTimeout(() => sendMessage(question), 100)
  }

  return (
    <div className="policy-chatbot">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <p>Ask me questions about this policy and its implementation.</p>
            <div className="suggested-questions">
              <p>Try asking:</p>
              <ul>
                {suggestedQuestions.map((q, idx) => (
                  <li key={idx} onClick={() => handleSuggestedQuestion(q)}>
                    {q}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.content}
            </div>
            <div className="message-time">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-content">Thinking...</div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about the policy..."
          className="chat-input"
          disabled={loading || !sessionId}
        />
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !sessionId || !input.trim()}
        >
          Send
        </button>
      </form>
    </div>
  )
}

export default PolicyChatbot
