from flask import Blueprint, jsonify, request
import logging
from database import DatabaseOperations
from utils.telegram_notifier import telegram_notifier

logger = logging.getLogger(__name__)

telegram_bp = Blueprint('telegram', __name__)

@telegram_bp.route('/verify-bot', methods=['POST'])
def verify_bot():
    """Verify Telegram bot token configuration"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        if not telegram_notifier.is_enabled():
            return jsonify({
                'error': 'Telegram bot not configured',
                'message': 'Please set TELEGRAM_BOT_TOKEN environment variable'
            }), 400

        # Verify bot token
        is_valid = telegram_notifier.verify_bot_token()

        if is_valid:
            bot_info = telegram_notifier.get_bot_info()
            return jsonify({
                'status': 'success',
                'enabled': True,
                'bot_info': {
                    'id': bot_info.get('id'),
                    'username': bot_info.get('username'),
                    'first_name': bot_info.get('first_name'),
                    'can_join_groups': bot_info.get('can_join_groups'),
                    'can_read_all_group_messages': bot_info.get('can_read_all_group_messages')
                } if bot_info else None
            })
        else:
            return jsonify({
                'error': 'Invalid bot token',
                'message': 'The provided TELEGRAM_BOT_TOKEN is invalid'
            }), 400

    except Exception as e:
        logger.error(f"Error verifying bot: {str(e)}")
        return jsonify({'error': str(e)}), 500

@telegram_bp.route('/connect', methods=['POST'])
def connect_telegram():
    """Connect Telegram chat ID to user account"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        telegram_chat_id = data.get('telegram_chat_id')
        if not telegram_chat_id:
            return jsonify({'error': 'telegram_chat_id is required'}), 400

        # Update user's Telegram chat ID
        user = DatabaseOperations.update_user_telegram_chat(user_id, str(telegram_chat_id))

        if not user:
            return jsonify({'error': 'Failed to connect Telegram'}), 500

        # Send a test message to verify connection
        test_message_sent = telegram_notifier.send_message(
            telegram_chat_id,
            "✅ <b>Telegram notifications enabled!</b>\n\nYou will receive notifications when your async tasks complete.",
            parse_mode='HTML'
        )

        return jsonify({
            'status': 'success',
            'message': 'Telegram connected successfully',
            'test_message_sent': test_message_sent
        })

    except Exception as e:
        logger.error(f"Error connecting Telegram: {str(e)}")
        return jsonify({'error': str(e)}), 500

@telegram_bp.route('/disconnect', methods=['POST'])
def disconnect_telegram():
    """Disconnect Telegram from user account"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        # Remove user's Telegram chat ID
        user = DatabaseOperations.remove_user_telegram_chat(user_id)

        if not user:
            return jsonify({'error': 'Failed to disconnect Telegram'}), 500

        return jsonify({
            'status': 'success',
            'message': 'Telegram disconnected successfully'
        })

    except Exception as e:
        logger.error(f"Error disconnecting Telegram: {str(e)}")
        return jsonify({'error': str(e)}), 500

@telegram_bp.route('/status', methods=['GET'])
def get_telegram_status():
    """Get user's Telegram connection status"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        # Get user's Telegram chat ID
        chat_id = DatabaseOperations.get_user_telegram_chat_id(user_id)

        # Check if bot is configured
        bot_enabled = telegram_notifier.is_enabled()

        bot_info = None
        if bot_enabled:
            bot_info = telegram_notifier.get_bot_info()

        return jsonify({
            'status': 'success',
            'telegram': {
                'enabled': bot_enabled,
                'connected': bool(chat_id),
                'chat_id': chat_id if chat_id else None,
                'bot_info': {
                    'username': bot_info.get('username'),
                    'first_name': bot_info.get('first_name')
                } if bot_info else None
            }
        })

    except Exception as e:
        logger.error(f"Error getting Telegram status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@telegram_bp.route('/send-test', methods=['POST'])
def send_test_message():
    """Send a test message to user's Telegram"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        # Get user's Telegram chat ID
        chat_id = DatabaseOperations.get_user_telegram_chat_id(user_id)

        if not chat_id:
            return jsonify({
                'error': 'Telegram not connected',
                'message': 'Please connect your Telegram account first'
            }), 400

        # Send test message
        success = telegram_notifier.send_message(
            chat_id,
            "🔔 <b>Test Notification</b>\n\nThis is a test message from your async code platform.\nYour Telegram notifications are working correctly!",
            parse_mode='HTML'
        )

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Test message sent successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to send test message',
                'message': 'Please check your Telegram chat ID and bot configuration'
            }), 500

    except Exception as e:
        logger.error(f"Error sending test message: {str(e)}")
        return jsonify({'error': str(e)}), 500