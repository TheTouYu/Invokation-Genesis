import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { GameState } from '../types/game';

const initialState: { gameState: GameState | null; error: string | null } = {
  gameState: null,
  error: null,
};

const gameSlice = createSlice({
  name: 'game',
  initialState,
  reducers: {
    setGameState: (state, action: PayloadAction<GameState>) => {
      state.gameState = action.payload;
      state.error = null;
    },
    updateGameState: (state, action: PayloadAction<Partial<GameState>>) => {
      if (state.gameState) {
        state.gameState = { ...state.gameState, ...action.payload };
      }
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const { setGameState, updateGameState, setError, clearError } = gameSlice.actions;
export default gameSlice.reducer;