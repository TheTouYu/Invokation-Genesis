import { configureStore } from '@reduxjs/toolkit';
import gameReducer from './gameSlice';
import authReducer from './authSlice';

export const store = configureStore({
  reducer: {
    game: gameReducer,
    auth: authReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['game/setGameState'],
        ignoredPaths: ['game.gameState'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;