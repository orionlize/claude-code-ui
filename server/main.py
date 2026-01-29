from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging
import os
from dotenv import load_dotenv
from tasks import tasks_bp
from projects import projects_bp
from health import health_bp
from websocket_manager import websocket_manager

# Import websocket manager setter
from utils.code_task_v2 import set_websocket_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
# Configure CORS
CORS(app, origins=['http://localhost:3000', 'https://*.vercel.app'])

# Initialize SocketIO with CORS
socketio = SocketIO(
    app,
    cors_allowed_origins=['http://localhost:3000', 'https://*.vercel.app'],
    async_mode='threading',
    logger=False,
    engineio_logger=False
)

# Set websocket manager for code_task_v2
set_websocket_manager(websocket_manager)

# Register blueprints
app.register_blueprint(health_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(projects_bp)


# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"🔌 Client connected: {request.sid}")
    emit('connected', {'status': 'connected', 'sid': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"🔌 Client disconnected: {request.sid}")
    websocket_manager.disconnect_session(request.sid)


@socketio.on('subscribe_task')
def handle_subscribe_task(data):
    """Handle subscription to a specific task"""
    task_id = data.get('task_id')
    if not task_id:
        emit('error', {'message': 'task_id is required'})
        return

    success = websocket_manager.subscribe_to_task(task_id, request.sid)

    if success:
        emit('subscribed', {'task_id': task_id, 'message': f'Subscribed to task {task_id}'})
    else:
        emit('error', {'message': 'Failed to subscribe to task'})


@socketio.on('unsubscribe_task')
def handle_unsubscribe_task(data):
    """Handle unsubscription from a specific task"""
    task_id = data.get('task_id')
    if not task_id:
        emit('error', {'message': 'task_id is required'})
        return

    success = websocket_manager.unsubscribe_from_task(task_id, request.sid)

    if success:
        emit('unsubscribed', {'task_id': task_id, 'message': f'Unsubscribed from task {task_id}'})
    else:
        emit('error', {'message': 'Failed to unsubscribe from task'})


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask-SocketIO server on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)