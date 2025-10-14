import { SocketType } from 'dgram';
import io from 'socket.io-client';
import { Socket } from 'socket.io-client';
import { GameAction } from '../types/game';

class WebsocketService {
  private socket: typeof Socket | null = null;
  private baseUrl: string = process.env.REACT_APP_WS_URL || 'http://localhost:5000';

  connect(gameId: string, playerId: string, token?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      // Cast the return value of io() to Socket type
      this.socket = io(this.baseUrl, {
        transports: ['websocket'],
        auth: {
          gameId,
          playerId,
          token,
        },
      })

      this.socket.on('connect', () => {
        console.log('Connected to game server');
        resolve();
      });

      this.socket.on('connect_error', (error: Error) => {
        console.error('Connection error:', error);
        reject(error);
      });

      this.socket.on('disconnect', (reason: string) => {
        console.log('Disconnected from game server:', reason);
      });
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // Game events
  onGameUpdate(callback: (gameState: any) => void): void {
    if (this.socket) {
      this.socket.on('gameUpdate', callback);
    }
  }

  onGameError(callback: (error: string) => void): void {
    if (this.socket) {
      this.socket.on('gameError', callback);
    }
  }

  onGameEnd(callback: (result: any) => void): void {
    if (this.socket) {
      this.socket.on('gameEnd', callback);
    }
  }

  // Send game actions
  sendAction(action: GameAction): void {
    if (this.socket) {
      this.socket.emit('gameAction', action);
    }
  }

  // Multiplayer game management
  createGame(): void {
    if (this.socket) {
      this.socket.emit('createGame');
    }
  }

  joinGame(gameId: string): void {
    if (this.socket) {
      this.socket.emit('joinGame', gameId);
    }
  }

  leaveGame(): void {
    if (this.socket) {
      this.socket.emit('leaveGame');
    }
  }

  // Matchmaking
  joinMatchmaking(): void {
    if (this.socket) {
      this.socket.emit('joinMatchmaking');
    }
  }

  leaveMatchmaking(): void {
    if (this.socket) {
      this.socket.emit('leaveMatchmaking');
    }
  }
}

export default new WebsocketService();
