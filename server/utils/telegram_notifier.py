import os
import logging
import requests
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Telegram bot notification handler for task completion alerts"""

    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.enabled = bool(self.bot_token)

        if self.enabled:
            logger.info("✅ Telegram notifications enabled")
        else:
            logger.info("ℹ️  Telegram notifications disabled (TELEGRAM_BOT_TOKEN not set)")

    def is_enabled(self) -> bool:
        """Check if Telegram notifications are enabled"""
        return self.enabled

    def send_message(self, chat_id: str, message: str, parse_mode: str = 'HTML') -> bool:
        """
        Send a message to a Telegram chat

        Args:
            chat_id: Telegram chat ID to send message to
            message: Message content
            parse_mode: Parse mode (HTML, Markdown, or None)

        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Telegram notifications disabled, skipping message")
            return False

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }

            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

            logger.info(f"✅ Telegram message sent to chat {chat_id}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")
            return False

    def notify_task_completed(self, chat_id: str, task: Dict, repo_url: str,
                             status: str = 'completed', error: Optional[str] = None) -> bool:
        """
        Send task completion notification to Telegram

        Args:
            chat_id: Telegram chat ID
            task: Task dictionary with task details
            repo_url: Repository URL
            status: Task status ('completed' or 'failed')
            error: Error message if task failed

        Returns:
            bool: True if notification sent successfully
        """
        if not self.enabled:
            return False

        try:
            # Get prompt from chat messages
            prompt = ""
            if task.get('chat_messages'):
                for msg in task['chat_messages']:
                    if msg.get('role') == 'user':
                        prompt = msg.get('content', '')
                        break

            # Truncate prompt if too long
            prompt_display = prompt[:100] + '...' if len(prompt) > 100 else prompt

            # Extract repo name from URL
            repo_name = repo_url.split('/')[-1].replace('.git', '') if repo_url else 'Unknown'

            # Build message based on status
            if status == 'completed':
                emoji = "✅"
                status_text = "Completed Successfully"

                # Get changed files count
                changed_files = task.get('changed_files', [])
                files_count = len(changed_files) if changed_files else 0

                # Build success message
                message = f"""
{emoji} <b>Task Completed</b>

<b>Repository:</b> {repo_name}
<b>Task ID:</b> {task.get('id', 'N/A')}
<b>Prompt:</b> {prompt_display}

<b>Results:</b>
• Files changed: {files_count}
• Commit: {task.get('commit_hash', 'N/A')[:8] if task.get('commit_hash') else 'N/A'}

<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            else:
                emoji = "❌"
                status_text = "Failed"
                error_msg = error[:200] + '...' if error and len(error) > 200 else (error or 'Unknown error')

                message = f"""
{emoji} <b>Task Failed</b>

<b>Repository:</b> {repo_name}
<b>Task ID:</b> {task.get('id', 'N/A')}
<b>Prompt:</b> {prompt_display}

<b>Error:</b>
{error_msg}

<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            return self.send_message(chat_id, message.strip())

        except Exception as e:
            logger.error(f"❌ Failed to send task completion notification: {e}")
            return False

    def notify_pr_created(self, chat_id: str, task_id: int, pr_url: str,
                         repo_name: str, pr_number: int) -> bool:
        """
        Send notification when PR is created

        Args:
            chat_id: Telegram chat ID
            task_id: Task ID
            pr_url: Pull request URL
            repo_name: Repository name
            pr_number: Pull request number

        Returns:
            bool: True if notification sent successfully
        """
        if not self.enabled:
            return False

        try:
            message = f"""
🔀 <b>Pull Request Created</b>

<b>Repository:</b> {repo_name}
<b>Task ID:</b> {task_id}
<b>PR Number:</b> #{pr_number}

<b>Link:</b> {pr_url}

<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            return self.send_message(chat_id, message.strip())

        except Exception as e:
            logger.error(f"❌ Failed to send PR notification: {e}")
            return False

    def verify_bot_token(self) -> bool:
        """
        Verify that the bot token is valid

        Returns:
            bool: True if token is valid, False otherwise
        """
        if not self.enabled:
            return False

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                logger.info(f"✅ Bot token verified: @{bot_info.get('username', 'unknown')}")
                return True
            else:
                logger.error(f"❌ Invalid bot token: {data.get('description', 'Unknown error')}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to verify bot token: {e}")
            return False

    def get_bot_info(self) -> Optional[Dict]:
        """
        Get bot information

        Returns:
            Dict with bot info or None if failed
        """
        if not self.enabled:
            return None

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get('ok'):
                return data.get('result')
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to get bot info: {e}")
            return None

# Global instance
telegram_notifier = TelegramNotifier()