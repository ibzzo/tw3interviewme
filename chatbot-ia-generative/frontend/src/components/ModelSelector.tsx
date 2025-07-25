import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const SelectorContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 8px;
`;

const Label = styled.label`
  font-weight: 500;
  color: #333;
`;

const Select = styled.select`
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  
  &:hover {
    border-color: #007bff;
  }
`;

const StatusIndicator = styled.span<{ available: boolean }>`
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: ${props => props.available ? '#4caf50' : '#f44336'};
  margin-left: 5px;
`;

const StatusText = styled.span`
  font-size: 12px;
  color: #666;
  margin-left: 5px;
`;

interface ModelSelectorProps {
  onModelChange?: (model: string) => void;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({ onModelChange }) => {
  const [selectedModel, setSelectedModel] = useState<string>('openrouter');
  const [vllmStatus, setVllmStatus] = useState<boolean>(false);
  const [vllmModel, setVllmModel] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    checkVLLMStatus();
    // Vérifier le statut toutes les 10 secondes
    const interval = setInterval(checkVLLMStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkVLLMStatus = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/vllm/status/');
      setVllmStatus(response.data.available);
      setVllmModel(response.data.current_model || 'Phi-3-mini');
    } catch (error) {
      console.error('Error checking vLLM status:', error);
      setVllmStatus(false);
    }
  };

  const handleModelChange = async (event: React.ChangeEvent<HTMLSelectElement>) => {
    const model = event.target.value;
    setSelectedModel(model);
    setLoading(true);
    
    try {
      // Envoyer le choix au backend
      await axios.post('http://localhost:8000/api/v1/set-model/', {
        model: model
      });
      
      if (onModelChange) {
        onModelChange(model);
      }
    } catch (error) {
      console.error('Error setting model:', error);
    }
    
    setLoading(false);
  };

  return (
    <SelectorContainer>
      <Label htmlFor="model-select">Modèle IA :</Label>
      <Select
        id="model-select"
        value={selectedModel}
        onChange={handleModelChange}
        disabled={loading}
      >
        <option value="vllm">vLLM Local (Phi-3)</option>
        <option value="openrouter">OpenRouter Cloud (Qwen)</option>
      </Select>
      
      <StatusIndicator available={selectedModel === 'vllm' ? vllmStatus : true} />
      
      <StatusText>
        {loading && 'Changement...'}
        {!loading && selectedModel === 'vllm' && (vllmStatus ? '✅ Local actif' : '❌ Local indisponible')}
        {!loading && selectedModel === 'openrouter' && '☁️ Cloud actif'}
      </StatusText>
    </SelectorContainer>
  );
};

export default ModelSelector;