from database import DatabaseOperations
import fcntl

from utils.telegram_notifier import telegram_notifier
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
                }
            })
            
            # Send Telegram notification
            send_task_completion_notification(task_id, user_id, 'completed')
            logger.info(f"🎉 {model_name} Task {task_id} completed successfully! Commit: {commit_hash[:8] if commit_hash else 'N/A'}, Diff lines: {len(git_diff)}")
            
        else:
                'error': f"Container exited with code {result['StatusCode']}: {logs}"
            })
            logger.error(f"💥 {model_name} Task {task_id} failed: {logs[:200]}...")
            # Send Telegram notification for failure
            send_task_completion_notification(task_id, user_id, 'failed', f"Container exited with code {result["'StatusCode'"]}: {logs[:200]}")
            
    except Exception as e:
        model_name = task.get('agent', 'claude').upper() if task else 'UNKNOWN'
            logger.error(f"Failed to update task {task_id} status after exception")
        
        logger.error(f"🔄 {model_name} Task {task_id} failed with exception: {str(e)}")
        # Send Telegram notification for exception
        send_task_completion_notification(task_id, user_id, 'failed', str(e))

def send_task_completion_notification(task_id: int, user_id: str, status: str, error: str = None):
    """Send Telegram notification when task completes"""
    try:
        # Get user's Telegram chat ID
        from database import DatabaseOperations
        chat_id = DatabaseOperations.get_user_telegram_chat_id(user_id)

        if not chat_id:
            logger.debug(f"No Telegram chat ID for user {user_id}, skipping notification")
            return

        # Get task details
        task = DatabaseOperations.get_task_by_id(task_id, user_id)
        if not task:
            logger.warning(f"Task {task_id} not found, cannot send notification")
            return

        # Send notification
        telegram_notifier.notify_task_completed(
            chat_id=chat_id,
            task=task,
            repo_url=task.get('repo_url', ''),
            status=status,
            error=error
        )

    except Exception as e:
        # Don't fail the task if notification fails
        logger.error(f"Failed to send Telegram notification: {e}")