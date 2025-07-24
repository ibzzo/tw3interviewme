import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  padding: 0;
  background: #ffffff;
  height: 100%;
  overflow: hidden;
`;

const MessagesColumn = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  overflow: hidden;
`;

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  sources?: Array<{title: string; url: string; snippet?: string}>;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (content: string) => {
    // Add user message to the list
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      created_at: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/v1/chat/', {
        message: content,
        conversation_id: conversationId
      });

      const { conversation_id, message, sources } = response.data;
      
      // Update conversation ID if new
      if (!conversationId && conversation_id) {
        setConversationId(conversation_id);
      }
      
      // Le message assistant est déjà formaté par le backend
      const assistantMessage: Message = {
        id: message.id,
        role: message.role,
        content: message.content,
        created_at: message.created_at,
        sources: message.sources || sources
      };
      
      // Add assistant message
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Désolé, une erreur s\'est produite. Veuillez réessayer.',
        created_at: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ChatContainer>
      <MessagesColumn>
        <MessageList messages={messages} loading={loading} />
        <div ref={messagesEndRef} />
      </MessagesColumn>
      <MessageInput onSendMessage={sendMessage} disabled={loading} />
    </ChatContainer>
  );
};

export default ChatInterface;