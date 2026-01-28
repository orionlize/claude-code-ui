# Telegram Bot Notification Setup Guide

This guide explains how to configure Telegram bot notifications for async task completion alerts.

## Overview

When enabled, the system will send Telegram notifications when:
- ✅ Async tasks complete successfully
- ❌ Async tasks fail or encounter errors
- 🔀 Pull requests are created from task results

## Prerequisites

1. A Telegram account
2. Access to the server environment variables

## Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts to:
   - Choose a bot name (e.g., "My Code Tasks Bot")
   - Choose a username (e.g., `my_code_tasks_bot`)
4. Copy the **bot token** provided (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Configure Server Environment

Add the bot token to your server environment:

```bash
# Add to .env file
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

Or set as environment variable:

```bash
export TELEGRAM_BOT_TOKEN=your_bot_token_here
```

Restart your Flask server after setting the token.

## Step 3: Get Your Telegram Chat ID

1. Start a conversation with your bot by sending it a message (e.g., "start")
2. Visit this URL in your browser:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. Look for `"chat":{"id":123456789}` in the response
4. Copy the numeric ID

**Alternative Method**: Use a bot like `@userinfobot` to get your chat ID.

## Step 4: Connect Your Account

Use the API to connect your Telegram chat ID to your account:

```bash
curl -X POST http://your-server:5000/telegram/connect \
  -H "Content-Type: application/json" \
  -H "X-User-ID: your-user-id" \
  -d '{
    "telegram_chat_id": "123456789"
  }'
```

Or via frontend (if implemented):
- Go to Settings → Notifications
- Enter your Telegram Chat ID
- Click "Connect Telegram"

## Step 5: Test Notifications

Send a test message to verify everything is working:

```bash
curl -X POST http://your-server:5000/telegram/send-test \
  -H "X-User-ID: your-user-id"
```

You should receive a test message in Telegram.

## API Endpoints

### Verify Bot Configuration
```http
POST /telegram/verify-bot
Headers: X-User-ID: your-user-id
```

Returns bot information if configured correctly.

### Connect Telegram
```http
POST /telegram/connect
Headers: 
  X-User-ID: your-user-id
  Content-Type: application/json
Body: {
  "telegram_chat_id": "123456789"
}
```

### Disconnect Telegram
```http
POST /telegram/disconnect
Headers: X-User-ID: your-user-id
```

### Get Status
```http
GET /telegram/status
Headers: X-User-ID: your-user-id
```

Returns current connection status and bot information.

### Send Test Message
```http
POST /telegram/send-test
Headers: X-User-ID: your-user-id
```

## Notification Format

### Task Completed
```
✅ Task Completed

Repository: my-repo
Task ID: 123
Prompt: Fix the login bug...

Results:
• Files changed: 3
• Commit: a1b2c3d4

Time: 2025-01-28 14:30:00
```

### Task Failed
```
❌ Task Failed

Repository: my-repo
Task ID: 124
Prompt: Add new feature...

Error:
Container execution timeout or error:...

Time: 2025-01-28 14:35:00
```

### Pull Request Created
```
🔀 Pull Request Created

Repository: my-repo
Task ID: 123
PR Number: #42

Link: https://github.com/owner/repo/pull/42

Time: 2025-01-28 14:40:00
```

## Troubleshooting

### Bot Not Responding
- Verify bot token is correct: `curl https://api.telegram.org/bot<TOKEN>/getMe`
- Check server logs for errors
- Ensure bot token is set in environment variables

### Not Receiving Notifications
- Verify chat ID is correct
- Check that you've started a conversation with the bot
- Use `/send-test` endpoint to test connection
- Check server logs for sending errors

### Bot Token Invalid
- Regenerate token from @BotFather
- Ensure no extra spaces in token
- Verify token format: `numbers:letters`

## Security Considerations

1. **Keep bot token secret** - Anyone with the token can control your bot
2. **Use environment variables** - Never commit tokens to code
3. **Limit bot permissions** - Don't enable unnecessary features in @BotFather
4. **Monitor usage** - Check bot statistics regularly

## Optional Enhancements

### Enable Privacy Mode
In @BotFather, use:
```
/setprivacy
```
Choose your bot, then select "Enable" to limit bot commands only to users who explicitly interact with it.

### Set Bot Description
```
/setdescription
```
Add a helpful description for users.

### Set Bot Commands
```
/setcommands
```
Configure command menu (e.g., start, help, status).

## Database Schema

The system stores Telegram chat IDs in the `users` table:

```sql
users {
  id: uuid
  preferences: jsonb {
    telegram_chat_id: string
  }
}
```

## Example Code Integration

```python
from utils.telegram_notifier import telegram_notifier
from database import DatabaseOperations

# Get user's chat ID
chat_id = DatabaseOperations.get_user_telegram_chat_id(user_id)

# Send custom notification
telegram_notifier.send_message(
    chat_id=chat_id,
    message="Your custom message here",
    parse_mode='HTML'
)
```

## Support

For issues or questions:
1. Check server logs: `docker logs <container>`
2. Verify bot token: `/telegram/verify-bot` endpoint
3. Test connection: `/telegram/send-test` endpoint
4. Check Telegram API status: https://status.telegram.org/