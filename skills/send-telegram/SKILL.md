---
name: send-telegram
description: Send messages to Telegram chats via bot API with automatic message chunking for long content. Use when agent needs to send notifications, alerts, logs, status updates, or any text content to Telegram. Handles message length limits automatically by splitting long messages into numbered chunks.
---

# Send Telegram

## Overview

Send text messages to Telegram chats using the Telegram Bot API. Automatically handles long messages by chunking them into multiple parts with pagination headers (1/3, 2/3, etc.).

## Quick Start

Use the `send_telegram.sh` script to send messages:

```bash
# Send a simple message
./scripts/send_telegram.sh "Hello from Claude!"

# Send a long message (will be automatically chunked)
./scripts/send_telegram.sh "Very long message content..."

# Send from stdin
echo "Message content" | ./scripts/send_telegram.sh

# Send file contents
cat log.txt | ./scripts/send_telegram.sh
```

## Environment Variables

Required environment variables (must be set before using):

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `TELEGRAM_CHAT_ID`: Target chat ID (user, group, or channel ID)

Optional environment variables:

- `MAX_LEN`: Maximum message length per chunk (default: 3900)
- `DISABLE_WEB_PAGE_PREVIEW`: Disable link previews (default: true)
- `DISABLE_NOTIFICATION`: Send silently (default: false)

## Usage Examples

**Sending notifications:**
```bash
./scripts/send_telegram.sh "🚀 Build completed successfully!"
```

**Sending logs or reports:**
```bash
# Large content will be automatically split
./scripts/send_telegram.sh "$(cat build_report.txt)"
```

**With HTML formatting:**
```bash
./scripts/send_telegram.sh "<b>Alert:</b> System status is <i>healthy</i>"
```

## Features

- **Automatic chunking**: Long messages split into multiple parts with headers
- **HTML support**: Use HTML tags for formatting (bold, italic, etc.)
- **Flexible input**: Accept message as arguments or from stdin
- **Error handling**: Validates API responses and provides clear error messages
- **Configurable**: Customize message length, notifications, and previews
