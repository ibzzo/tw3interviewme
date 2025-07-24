import React, { useState, KeyboardEvent } from 'react';
import styled from 'styled-components';

const InputContainer = styled.div`
  display: flex;
  gap: 0.5rem;
  padding: 1rem 2rem 2rem;
  background: white;
  border-top: 1px solid #e5e7eb;
`;

const InputWrapper = styled.div`
  flex: 1;
  position: relative;
`;

const TextArea = styled.textarea`
  width: 100%;
  resize: none;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  font-family: inherit;
  font-size: 0.9375rem;
  min-height: 44px;
  max-height: 150px;
  background: #ffffff;
  transition: all 0.2s ease;
  
  &::placeholder {
    color: #9ca3af;
  }
  
  &:focus {
    outline: none;
    border-color: #6b7280;
  }
  
  &:disabled {
    background-color: #f9fafb;
    cursor: not-allowed;
    opacity: 0.7;
  }
`;

const SendButton = styled.button`
  padding: 0.5rem 1rem;
  background: #1f2937;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  
  &:hover:not(:disabled) {
    background: #374151;
  }
  
  &:active:not(:disabled) {
    background: #111827;
  }
  
  &:disabled {
    background: #d1d5db;
    cursor: not-allowed;
  }
  
  svg {
    width: 18px;
    height: 18px;
  }
`;

const CharCount = styled.span`
  position: absolute;
  bottom: 0.5rem;
  right: 1rem;
  font-size: 0.75rem;
  color: #94a3b8;
`;

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <InputContainer>
      <InputWrapper>
        <TextArea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Posez votre question..."
          disabled={disabled}
          rows={2}
        />
        {message.length > 0 && (
          <CharCount>{message.length}/1000</CharCount>
        )}
      </InputWrapper>
      <SendButton onClick={handleSend} disabled={disabled || !message.trim()}>
        {disabled ? (
          <>Envoi...</>
        ) : (
          <>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </>
        )}
      </SendButton>
    </InputContainer>
  );
};

export default MessageInput;