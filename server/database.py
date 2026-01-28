            return result.data
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    @staticmethod
    def update_user_telegram_chat(user_id: str, telegram_chat_id: str) -> Optional[Dict]:
        """Update user's Telegram chat ID for notifications"""
        try:
            # Get current user
            user = DatabaseOperations.get_user_by_id(user_id)
            if not user:
                return None

            # Update preferences with Telegram chat ID
            preferences = user.get('preferences', {}) or {}
            preferences['telegram_chat_id'] = telegram_chat_id

            result = supabase.table('users').update({
                'preferences': preferences,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', user_id).execute()

            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error updating user Telegram chat ID: {e}")
            raise

    @staticmethod
    def get_user_telegram_chat_id(user_id: str) -> Optional[str]:
        """Get user's Telegram chat ID from preferences"""
        try:
            user = DatabaseOperations.get_user_by_id(user_id)
            if not user:
                return None

            preferences = user.get('preferences', {}) or {}
            return preferences.get('telegram_chat_id')
        except Exception as e:
            logger.error(f"Error getting user Telegram chat ID: {e}")
            return None

    @staticmethod
    def remove_user_telegram_chat(user_id: str) -> Optional[Dict]:
        """Remove user's Telegram chat ID (disable notifications)"""
        try:
            # Get current user
            user = DatabaseOperations.get_user_by_id(user_id)
            if not user:
                return None

            # Update preferences, removing Telegram chat ID
            preferences = user.get('preferences', {}) or {}
            if 'telegram_chat_id' in preferences:
                del preferences['telegram_chat_id']

            result = supabase.table('users').update({
                'preferences': preferences,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', user_id).execute()

            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error removing user Telegram chat ID: {e}")
            raise