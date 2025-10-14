import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Cards API
  getCharacters: () => api.get('/characters'),
  getEquipments: () => api.get('/equipments'),
  getSupports: () => api.get('/supports'),
  getEvents: () => api.get('/events'),

  // Game API
  startLocalGame: (deck: string[]) => api.post('/local-game/start', { deck }),
  makeGameAction: (sessionId: string, action: any) => 
    api.post(`/local-game/${sessionId}/action`, action),

  // Authentication API
  register: (userData: { username: string; password: string }) => 
    api.post('/auth/register', userData),
  login: (userData: { username: string; password: string }) => 
    api.post('/auth/login', userData),
  getProfile: () => api.get('/auth/profile'),

  // Deck API
  getDecks: () => api.get('/decks'),
  createDeck: (deckData: { name: string; cardIds: string[] }) => 
    api.post('/decks', deckData),
  updateDeck: (deckId: string, deckData: { name: string; cardIds: string[] }) => 
    api.put(`/decks/${deckId}`, deckData),
  deleteDeck: (deckId: string) => api.delete(`/decks/${deckId}`),
};

export default api;