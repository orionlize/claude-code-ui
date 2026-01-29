"""
WebSocket Manager for real-time task log streaming
"""
import logging
from typing import Dict, Set
from flask_socketio import emit, disconnect
from flask import request

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manage WebSocket connections and task log streaming"""

    def __init__(self):
        # Map task_id to set of connected session IDs
        self.task_connections: Dict[int, Set[str]] = {}
        # Map session_id to set of subscribed task_ids
        self.session_tasks: Dict[str, Set[int]] = {}

    def subscribe_to_task(self, task_id: int, sid: str = None):
        """Subscribe a client to receive logs for a specific task"""
        session_id = sid or request.sid

        if not session_id:
            logger.warning("Cannot subscribe: no session ID available")
            return False

        # Initialize sets if needed
        if task_id not in self.task_connections:
            self.task_connections[task_id] = set()
        if session_id not in self.session_tasks:
            self.session_tasks[session_id] = set()

        # Add subscription
        self.task_connections[task_id].add(session_id)
        self.session_tasks[session_id].add(task_id)

        logger.info(f"📡 Session {session_id} subscribed to task {task_id}")
        logger.info(f"📊 Task {task_id} now has {len(self.task_connections[task_id])} subscribers")

        return True

    def unsubscribe_from_task(self, task_id: int, sid: str = None):
        """Unsubscribe a client from a specific task"""
        session_id = sid or request.sid

        if not session_id:
            return False

        # Remove from task_connections
        if task_id in self.task_connections:
            self.task_connections[task_id].discard(session_id)
            if not self.task_connections[task_id]:
                del self.task_connections[task_id]
                logger.info(f"📊 Task {task_id} has no more subscribers")

        # Remove from session_tasks
        if session_id in self.session_tasks:
            self.session_tasks[session_id].discard(task_id)
            if not self.session_tasks[session_id]:
                del self.session_tasks[session_id]

        logger.info(f"📡 Session {session_id} unsubscribed from task {task_id}")
        return True

    def disconnect_session(self, sid: str = None):
        """Handle client disconnect - cleanup all subscriptions"""
        session_id = sid or request.sid

        if not session_id or session_id not in self.session_tasks:
            return

        # Get all tasks this session was subscribed to
        task_ids = list(self.session_tasks[session_id])

        # Remove session from all task subscriptions
        for task_id in task_ids:
            self.unsubscribe_from_task(task_id, session_id)

        logger.info(f"🔌 Session {session_id} disconnected, unsubscribed from {len(task_ids)} tasks")

    def broadcast_log(self, task_id: int, log_data: dict):
        """Broadcast log message to all subscribers of a task"""
        if task_id not in self.task_connections:
            # No subscribers for this task, skip broadcasting
            return

        # Get all subscribers for this task
        subscribers = list(self.task_connections[task_id])

        if not subscribers:
            return

        # Broadcast to all subscribers
        for session_id in subscribers:
            try:
                emit('task_log', log_data, to=session_id)
            except Exception as e:
                logger.error(f"❌ Failed to send log to session {session_id}: {e}")

        logger.debug(f"📤 Broadcast log to {len(subscribers)} subscribers for task {task_id}")

    def broadcast_status(self, task_id: int, status_data: dict):
        """Broadcast status update to all subscribers of a task"""
        if task_id not in self.task_connections:
            return

        subscribers = list(self.task_connections[task_id])

        if not subscribers:
            return

        for session_id in subscribers:
            try:
                emit('task_status', status_data, to=session_id)
            except Exception as e:
                logger.error(f"❌ Failed to send status to session {session_id}: {e}")

        logger.info(f"📢 Broadcast status '{status_data.get('status')}' to {len(subscribers)} subscribers for task {task_id}")

    def get_subscriber_count(self, task_id: int) -> int:
        """Get the number of subscribers for a task"""
        return len(self.task_connections.get(task_id, set()))


# Global instance
websocket_manager = WebSocketManager()