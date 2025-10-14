import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';
import GameBoard from './components/GameBoard/GameBoard';
import Login from './components/Login/Login';
import Register from './components/Register/Register';
import DeckBuilder from './components/DeckBuilder/DeckBuilder';
import Lobby from './components/Lobby/Lobby';
import GamePage from './components/GamePage/GamePage';

const AppRouter = () => {
  return (
    <Provider store={store}>
      <Router>
        <Routes>
          <Route path="/" element={<Lobby />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/deck-builder" element={<DeckBuilder />} />
          <Route path="/game/:gameId" element={<GamePage />} />
          <Route path="/local-game" element={<GameBoard />} />
        </Routes>
      </Router>
    </Provider>
  );
};

export default AppRouter;