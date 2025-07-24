import React from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import { Components } from 'react-markdown';

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 2rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
`;

const MessageWrapper = styled.div<{ isUser: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  animation: fadeIn 0.3s ease-in;
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const MessageBubble = styled.div<{ isUser: boolean }>`
  max-width: ${props => props.isUser ? '70%' : '100%'};
  padding: ${props => props.isUser ? '0.75rem 1rem' : '0'};
  border-radius: ${props => props.isUser ? '12px' : '0'};
  background: ${props => props.isUser ? '#2d3748' : 'transparent'};
  color: ${props => props.isUser ? 'white' : '#1a1a1a'};
  
  p {
    margin: 0 0 1rem 0;
    line-height: 1.6;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  pre {
    background-color: #f5f5f5;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    margin: 0.5rem 0;
    border: 1px solid #e5e5e5;
  }
  
  code {
    background-color: ${props => props.isUser ? 'rgba(255,255,255,0.2)' : '#f3f4f6'};
    padding: 0.1rem 0.3rem;
    border-radius: 3px;
    font-size: 0.875em;
    font-family: 'Consolas', monospace;
  }
  
  ul, ol {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
  }
  
  h1, h2, h3, h4, h5, h6 {
    margin: 1rem 0 0.5rem 0;
    font-weight: 600;
  }
`;

const LoadingIndicator = styled.div`
  display: flex;
  gap: 0.3rem;
  padding: 0.75rem 0;
  
  span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #6b7280;
    animation: bounce 1.4s infinite ease-in-out both;
    
    &:nth-child(1) {
      animation-delay: -0.32s;
    }
    
    &:nth-child(2) {
      animation-delay: -0.16s;
    }
  }
  
  @keyframes bounce {
    0%, 80%, 100% {
      transform: scale(0);
      opacity: 0.5;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }
`;

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  sources?: Array<{title: string; url: string; snippet?: string}>;
}

interface MessageListProps {
  messages: Message[];
  loading: boolean;
}

const MessageList: React.FC<MessageListProps> = ({ messages, loading }) => {
  // Fonction pour nettoyer le contenu des messages
  const cleanMessageContent = (content: string, sources?: Array<{title: string; url: string; snippet?: string}>): string => {
    // Patterns à supprimer
    const patterns = [
      /\n\n📚\s*Sources consultées.*$/s,
      /\n\nSources consultées.*$/s,
      /\n\n📚\s*Sources\s*:.*$/s,
      /\n\nSources\s*:.*$/s,
      /\n\n##\s*Sources.*$/s,
      /\n\n###\s*Sources.*$/s,
    ];
    
    let cleaned = content;
    
    // Supprimer tout ce qui suit ces patterns
    for (const pattern of patterns) {
      const match = cleaned.match(pattern);
      if (match && match.index !== undefined) {
        cleaned = cleaned.substring(0, match.index);
        break;
      }
    }
    
    // Remplacer [Source: ...] par des numéros basés sur les sources disponibles
    if (sources && sources.length > 0) {
      sources.forEach((source, index) => {
        // Remplacer [Source: titre] par [index+1]
        const sourcePattern = new RegExp(`\\[Source:\\s*${source.title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\]`, 'gi');
        cleaned = cleaned.replace(sourcePattern, `[${index + 1}]`);
      });
    }
    
    // Supprimer les [Source: ...] restants
    cleaned = cleaned.replace(/\[Source:\s*[^\]]+\]/g, '');
    
    return cleaned.trim();
  };

  // Custom renderer pour transformer [1], [2], etc. en liens cliquables
  const createMarkdownComponents = (sources: Array<{title: string; url: string; snippet?: string}> | undefined): Partial<Components> => {
    return {
      text: ({ node, ...props }) => {
        const text = String(props.children);
        if (!sources || sources.length === 0) return <>{text}</>;
        
        // Regex pour trouver [1], [2], etc.
        const citationRegex = /\[(\d+)\]/g;
        const parts = text.split(citationRegex);
        
        const result = [];
        for (let i = 0; i < parts.length; i++) {
          if (i % 2 === 0) {
            // Texte normal
            result.push(parts[i]);
          } else {
            // Numéro de citation
            const sourceIndex = parseInt(parts[i]) - 1;
            if (sourceIndex >= 0 && sourceIndex < sources.length) {
              const source = sources[sourceIndex];
              result.push(
                <a
                  key={`citation-${i}`}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: '#0066cc',
                    textDecoration: 'none',
                    fontWeight: 500,
                    fontSize: '0.875em',
                    marginLeft: '2px',
                    marginRight: '2px'
                  }}
                  title={source.title}
                >
                  [{parts[i]}]
                </a>
              );
            } else {
              result.push(`[${parts[i]}]`);
            }
          }
        }
        
        return <>{result}</>;
      }
    };
  };

  return (
    <MessagesContainer>
      {messages.map((message) => (
        <MessageWrapper key={message.id} isUser={message.role === 'user'}>
          <MessageBubble isUser={message.role === 'user'}>
            <ReactMarkdown 
              components={createMarkdownComponents(message.sources)}
            >
              {cleanMessageContent(message.content, message.sources)}
            </ReactMarkdown>
          </MessageBubble>
        </MessageWrapper>
      ))}
      {loading && (
        <LoadingIndicator>
          <span></span>
          <span></span>
          <span></span>
        </LoadingIndicator>
      )}
    </MessagesContainer>
  );
};

export default MessageList;