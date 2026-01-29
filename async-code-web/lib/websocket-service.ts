import { io, Socket } from 'socket.io-client';

export interface TaskLogMessage {
  task_id: number;
  log: string;
  timestamp: number;
}

export interface TaskStatusMessage {
  task_id: number;
  status: string;
  message?: string;
}

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect(url: string = 'http://localhost:5000'): Promise<Socket> {
    return new Promise((resolve, reject) => {
      if (this.socket?.connected) {
        resolve(this.socket);
        return;
      }

      console.log('[WebSocket] Connecting to...', url);

      this.socket = io(url, {
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: 1000,
      });

      this.socket.on('connect', () => {
        console.log('[WebSocket] Connected with ID:', this.socket?.id);
        this.reconnectAttempts = 0;
        resolve(this.socket!);
      });

      this.socket.on('connect_error', (error) => {
        console.error('[WebSocket] Connection error:', error);
        this.reconnectAttempts++;
        
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          reject(new Error('Failed to connect to WebSocket server'));
        }
      });

      this.socket.on('disconnect', (reason) => {
        console.log('[WebSocket] Disconnected:', reason);
      });

      this.socket.on('error', (error) => {
        console.error('[WebSocket] Error:', error);
      });
    });
  }

  disconnect() {
    if (this.socket) {
      console.log('[WebSocket] Disconnecting...');
      this.socket.disconnect();
      this.socket = null;
    }
  }

  subscribeToTask(taskId: number, callback: (log: TaskLogMessage) => void) {
    if (!this.socket?.connected) {
      console.warn('[WebSocket] Not connected, cannot subscribe to task');
      return;
    }

    console.log(`[WebSocket] Subscribing to task ${taskId}`);

    // Subscribe to the task
    this.socket.emit('subscribe_task', { task_id: taskId });

    // Listen for task logs
    this.socket.on('task_log', (data: TaskLogMessage) => {
      if (data.task_id === taskId) {
        callback(data);
      }
    });

    // Listen for subscription confirmation
    this.socket.once('subscribed', (data) => {
      if (data.task_id === taskId) {
        console.log(`[WebSocket] Successfully subscribed to task ${taskId}`);
      }
    });
  }

  unsubscribeFromTask(taskId: number) {
    if (!this.socket?.connected) {
      return;
    }

    console.log(`[WebSocket] Unsubscribing from task ${taskId}`);
    this.socket.emit('unsubscribe_task', { task_id: taskId });
    this.socket.off('task_log');

    // Listen for unsubscription confirmation
    this.socket.once('unsubscribed', (data) => {
      if (data.task_id === taskId) {
        console.log(`[WebSocket] Successfully unsubscribed from task ${taskId}`);
      }
    });
  }

  onTaskStatus(callback: (status: TaskStatusMessage) => void) {
    if (!this.socket) {
      return;
    }

    this.socket.on('task_status', callback);
  }

  offTaskStatus(callback: (status: TaskStatusMessage) => void) {
    if (!this.socket) {
      return;
    }

    this.socket.off('task_status', callback);
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false;
  }

  getSocket(): Socket | null {
    return this.socket;
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();