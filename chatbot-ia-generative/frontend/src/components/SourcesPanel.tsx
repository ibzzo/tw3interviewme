import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const PanelContainer = styled.div<{ isOpen: boolean }>`
  position: fixed;
  right: ${props => props.isOpen ? '0' : '-400px'};
  top: 0;
  height: 100vh;
  width: 400px;
  background: #f8f9fa;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  transition: right 0.3s ease;
  display: flex;
  flex-direction: column;
  z-index: 1000;
`;

const PanelHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
`;

const Title = styled.h3`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
  
  &:hover {
    background: #f0f0f0;
    color: #333;
  }
`;

const ToggleButton = styled.button<{ isOpen: boolean }>`
  position: fixed;
  right: ${props => props.isOpen ? '410px' : '10px'};
  top: 50%;
  transform: translateY(-50%);
  background: #007bff;
  color: white;
  border: none;
  padding: 12px 16px;
  border-radius: 24px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
  transition: all 0.3s ease;
  z-index: 999;
  
  &:hover {
    background: #0056b3;
    box-shadow: 0 4px 12px rgba(0, 123, 255, 0.4);
  }
`;

const SourcesContent = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
`;

const SourceCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
`;

const SourceTitle = styled.a`
  display: block;
  font-weight: 600;
  color: #007bff;
  text-decoration: none;
  margin-bottom: 8px;
  font-size: 15px;
  
  &:hover {
    text-decoration: underline;
  }
`;

const SourceSnippet = styled.p`
  margin: 0;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
`;

const SourceUrl = styled.p`
  margin: 8px 0 0;
  font-size: 12px;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const NoSources = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #999;
`;

const Badge = styled.span`
  display: inline-block;
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  margin-top: 8px;
`;

interface Source {
  title: string;
  url: string;
  snippet?: string;
}

interface SourcesPanelProps {
  sources: Source[];
  messageId?: string;
}

const SourcesPanel: React.FC<SourcesPanelProps> = ({ sources, messageId }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [displayedSources, setDisplayedSources] = useState<Source[]>([]);

  useEffect(() => {
    if (sources && sources.length > 0) {
      setDisplayedSources(sources);
      setIsOpen(true); // Ouvrir automatiquement quand il y a des sources
    }
  }, [sources]);

  const togglePanel = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      <ToggleButton isOpen={isOpen} onClick={togglePanel}>
        {isOpen ? '📚 Sources' : `📚 Sources (${displayedSources.length})`}
      </ToggleButton>
      
      <PanelContainer isOpen={isOpen}>
        <PanelHeader>
          <Title>Sources de la réponse</Title>
          <CloseButton onClick={() => setIsOpen(false)}>×</CloseButton>
        </PanelHeader>
        
        <SourcesContent>
          {displayedSources.length > 0 ? (
            displayedSources.map((source, index) => (
              <SourceCard key={index}>
                <SourceTitle href={source.url} target="_blank" rel="noopener noreferrer">
                  {source.title}
                </SourceTitle>
                {source.snippet && (
                  <SourceSnippet>{source.snippet}</SourceSnippet>
                )}
                <SourceUrl>{source.url}</SourceUrl>
                <Badge>Source {index + 1}</Badge>
              </SourceCard>
            ))
          ) : (
            <NoSources>
              <p>Aucune source pour cette réponse</p>
              <p style={{ fontSize: '12px', marginTop: '10px' }}>
                Les sources apparaissent lorsque le chatbot effectue une recherche web
              </p>
            </NoSources>
          )}
        </SourcesContent>
      </PanelContainer>
    </>
  );
};

export default SourcesPanel;