# Telegram Notification Feature

## Overview

This server now supports Telegram bot notifications for async task completion. Users can receive real-time alerts when their tasks complete or fail.

## Files Added/Modified

### New Files
- `utils/telegram_notifier.py` - Core notification module
- `telegram.py` - Telegram API endpoints

### Modified Files
- `main.py` - Registered telegram_bp blueprint
- `database.py` - Added Telegram chat ID methods
- `utils/code_task_v2.py` - Integrated notification calls
- `.env.example` - Added TELEGRAM_BOT_TOKEN configuration

## Environment Variables

```env
# Telegram Bot Configuration (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

Get your bot token from @BotFather on Telegram.

## API Endpoints

All endpoints require `X-User-ID` header.

### POST /telegram/verify-bot
Verify bot token is valid and get bot information.

**Response:**
```json
{
  "status": "success",
  "enabled": true,
  "bot_info": {
    "id": 123456789,
    "username": "my_bot",
    "first_name": "My Bot"
  }
}
```

### POST /telegram/connect
Connect Telegram chat ID to user account.

**Request:**
```json
{
  "telegram_chat_id": "123456789"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Telegram connected successfully",
  "test_message_sent": true
}
```

### POST /telegram/disconnect
Disconnect Telegram from user account.

**Response:**
```json
{
  "status": "success",
  "message": "Telegram disconnected successfully"
}
```

### GET /telegram/status
Get user's Telegram connection status.

**Response:**
```json
{
  "status": "success",
  "telegram": {
    "enabled": true,
    "connected": true,
    "chat_id": "123456789",
    "bot_info": {
      "username": "my_bot",
      "first_name": "My Bot"
    }
  }
}
```

### POST /telegram/send-test
Send a test message to verify connection.

**Response:**
```json
{
  "status": "success",
  "message": "Test message sent successfully"
}
```

## Database Schema Updates

The `users` table's `preferences` JSONB column now supports:

```json
{
  "telegram_chat_id": "123456789",
  "claudeCode": {
    "env": {...},
    "credentials": {...}
  }
}
```

## Notification Triggers

Notifications are automatically sent when:

1. **Task Completes Successfully** (`utils/code_task_v2.py:678`)
   - After task execution completes
   - Includes commit hash, files changed, task details

2. **Task Fails** (`utils/code_task_v2.py:689`)
   - After container exits with error code
   - Includes error message and task details

3. **Task Exception** (`utils/code_task_v2.py:705`)
   - When unhandled exception occurs
   - Includes exception details

## Implementation Details

### Notification Flow

```
Task Completion → send_task_completion_notification()
                → DatabaseOperations.get_user_telegram_chat_id()
                → telegram_notifier.notify_task_completed()
                → Telegram Bot API → User's Telegram
```

### Error Handling

- Notification failures don't affect task execution
- Errors logged to server logs
- Returns early if no chat ID configured
- Returns early if bot not enabled

### Message Format

Messages use HTML parse_mode for formatting:
- `<b>` for bold
- Message limit: ~4096 characters (Telegram limit)
- Includes emojis for visual clarity

## Testing

### 1. Verify Bot Configuration
```bash
curl -X POST http://localhost:5000/telegram/verify-bot \
  -H "X-User-ID: test-user-id"
```

### 2. Connect Your Account
```bash
curl -X POST http://localhost:5000/telegram/connect \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user-id" \
  -d '{"telegram_chat_id": "YOUR_CHAT_ID"}'
```

### 3. Send Test Message
```bash
curl -X POST http://localhost:5000/telegram/send-test \
  -H "X-User-ID: test-user-id"
```

### 4. Trigger a Task
Start an async task and verify you receive a notification on completion.

## Frontend Integration

### Example: React Component

```jsx
import { useState, useEffect } from 'react';

export function TelegramSettings({ userId }) {
  const [status, setStatus] = useState(null);
  const [chatId, setChatId] = useState('');

  useEffect(() => {
    fetch(`http://localhost:5000/telegram/status`, {
      headers: { 'X-User-ID': userId }
    })
      .then(r => r.json())
      .then(data => setStatus(data.telegram));
  }, [userId]);

  const handleConnect = async () => {
    await fetch('http://localhost:5000/telegram/connect', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': userId
      },
      body: JSON.stringify({ telegram_chat_id: chatId })
    });
  };

  return (
    <div>
      <h3>Telegram Notifications</h3>
      {status?.connected ? (
        <p>✅ Connected: {status.chat_id}</p>
      ) : (
        <input
          value={chatId}
          onChange={e => setChatId(e.target.value)}
          placeholder="Enter Telegram Chat ID"
        />
      )}
      <button onClick={handleConnect}>
        {status?.connected ? 'Connected' : 'Connect'}
      </button>
    </div>
  );
}
```

## Security Considerations

1. **Bot Token Protection**
   - Never log the bot token
   - Use environment variables only
   - Rotate tokens periodically

2. **User Privacy**
   - Chat IDs are user-specific
   - No cross-user notifications
   - Stored securely in database

3. **Rate Limiting**
   - Telegram has rate limits (30 messages/second)
   - Consider implementing queue for bulk notifications
   - Handle rate limit errors gracefully

## Troubleshooting

### Bot Not Sending Messages
1. Check bot token is set: `echo $TELEGRAM_BOT_TOKEN`
2. Verify bot token: `/telegram/verify-bot` endpoint
3. Check server logs for errors
4. Ensure chat ID is correct

### "Chat not found" Error
- User must start conversation with bot first
- Chat ID must be numeric (not username)
- Bot must be member of group (for group chats)

### Notifications Not Received
1. Verify chat ID in database
2. Check `/telegram/status` endpoint
3. Use `/telegram/send-test` to test
4. Check Telegram app notifications are enabled

## Future Enhancements

Potential improvements:
- [ ] Group chat notifications
- [ ] Custom notification preferences per task
- [ ] Rich formatting with buttons (inline keyboards)
- [ ] Task progress updates (streaming)
- [ ] Multiple notification channels (Slack, Discord, etc.)
- [ ] Notification history/queue
- [ ] Webhook integration for custom actions