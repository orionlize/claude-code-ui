from datetime import datetime
from database import DatabaseOperations
import fcntl
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
# Docker client
docker_client = docker.from_env()

# Global reference to websocket manager (will be set by main app)
websocket_manager = None

def set_websocket_manager(manager):
    """Set the global websocket manager instance"""
    global websocket_manager
    websocket_manager = manager

def stream_container_logs(container, task_id: int, user_id: str):
    """Stream container logs in real-time via WebSocket"""
    try:
        if not websocket_manager:
            logger.debug("No websocket manager available, skipping log streaming")
            return

        logger.info(f"📡 Starting log stream for task {task_id}")

        # Stream logs from container
        log_generator = container.logs(stream=True, follow=True)

        for log_line in log_generator:
            try:
                # Decode log line
                log_text = log_line.decode('utf-8', errors='ignore').rstrip('\n\r')

                if not log_text:
                    continue

                # Broadcast log via WebSocket
                websocket_manager.broadcast_log(task_id, {
                    'task_id': task_id,
                    'log': log_text,
                    'timestamp': time.time()
                })

                # Throttle slightly to avoid overwhelming the client
                time.sleep(0.01)

            except Exception as e:
                logger.error(f"❌ Error processing log line: {e}")

        logger.info(f"📡 Log stream completed for task {task_id}")

    except Exception as e:
        logger.error(f"❌ Error in log streaming thread: {e}")


def cleanup_orphaned_containers():
    """Clean up orphaned AI code task containers aggressively"""
    try:
        
        # Update task with container ID (v2 function)
        DatabaseOperations.update_task(task_id, user_id, {'container_id': container.id})

        logger.info(f"⏳ Waiting for container to complete (timeout: 300s)...")

        # Notify WebSocket subscribers that task is running
        if websocket_manager:
            websocket_manager.broadcast_status(task_id, {
                'task_id': task_id,
                'status': 'running',
                'message': 'Container started, executing task...'
            })

        # Wait for container to finish - should exit naturally when script completes
        try:
            logger.info(f"🔄 Waiting for container script to complete naturally...")

            # Check initial container state
            container.reload()
            logger.info(f"🔍 Container initial state: {container.status}")

            # Start a thread to stream logs in real-time
            log_stream_thread = threading.Thread(
                target=stream_container_logs,
                args=(container, task_id, user_id)
            )
            log_stream_thread.daemon = True
            log_stream_thread.start()

            # Use standard wait - container should exit when bash script finishes
            logger.info(f"🔄 Calling container.wait() - container should exit when script completes...")
            result = container.wait(timeout=1800)  # 30 minute timeout
            logger.info(f"🎯 Container exited naturally! Exit code: {result['StatusCode']}")

            # Wait a bit for log streaming to complete
            log_stream_thread.join(timeout=2)
            
            # Verify final container state
            container.reload()