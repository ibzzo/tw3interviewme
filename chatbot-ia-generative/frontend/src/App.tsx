import React from 'react';
import ChatInterface from './components/ChatInterface';
import ModelSelector from './components/ModelSelector';
import styled from 'styled-components';

const AppContainer = styled.div`
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  overflow: hidden;
`;

const Header = styled.header`
  background-color: #ffffff;
  color: #1a1a1a;
  padding: 1rem 2rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08);
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
  position: relative;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h1`
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
`;

function App() {
  return (
    <AppContainer>
      <Header>
        <Title>AI Chatbot avec Recherche Web</Title>
        <ModelSelector />
      </Header>
      <ChatInterface />
    </AppContainer>
  );
}

export default App;
