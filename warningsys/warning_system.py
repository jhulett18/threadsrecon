import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging
from datetime import datetime

class TelegramAlertSystem:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.bot = None
        self.alert_levels = {
            'HIGH': '🔴',
            'MEDIUM': '🟡',
            'LOW': '🟢'
        }
        
    async def initialize(self):
        """Initialize the bot"""
        self.bot = Bot(token=self.token)
        
    def escape_markdown(self, text):
        """Escape Markdown special characters"""
        # List of special characters that need to be escaped in MarkdownV2
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        escaped_text = str(text)
        for char in special_chars:
            escaped_text = escaped_text.replace(char, f'\\{char}')
        return escaped_text
        
    def truncate_text(self, text, max_length=200):
        """Truncate text and ensure it doesn't break Markdown formatting"""
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length].rstrip()
        # Ensure we're not breaking in the middle of a Markdown symbol
        if truncated.count('*') % 2 != 0:
            truncated = truncated.rstrip('*')
        return f"{truncated}..."
        
    async def send_alert(self, keyword, text, priority='LOW', metadata=None):
        """Send an alert message to Telegram"""
        if not self.bot:
            await self.initialize()
            
        timestamp = datetime.now().strftime('%Y\\-\\%m\\-\\%d %H:%M:%S')  # Escape dashes in date
        emoji = self.alert_levels.get(priority.upper(), '⚪')
        
        # Escape all text fields
        safe_keyword = self.escape_markdown(str(keyword))
        safe_text = self.escape_markdown(str(text))
        safe_text = self.truncate_text(safe_text)
        
        message_parts = [
            f"{emoji} *ALERT* {emoji}",
            f"*Priority*: {priority}",
            f"*Keyword*: {safe_keyword}",
            f"*Time*: {timestamp}",
            f"*Content*: {safe_text}"
        ]
        
        if metadata:
            message_parts.append("\n*Additional Info*:")
            for key, value in metadata.items():
                safe_key = self.escape_markdown(str(key))
                safe_value = self.escape_markdown(str(value))
                # Use bullet point instead of hyphen for lists
                message_parts.append(f"• {safe_key}: {safe_value}")
        
        message = '\n'.join(message_parts)
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='MarkdownV2'
            )
            return True
        except Exception as e:
            logging.error(f"Failed to send Telegram alert: {str(e)}")
            # Log the actual message for debugging
            logging.debug(f"Attempted to send message: {message}")
            return False


class KeywordMonitor:
    def __init__(self, telegram_token, chat_id, priority_keywords=None):
        self.alert_system = TelegramAlertSystem(telegram_token, chat_id)
        self.priority_keywords = priority_keywords or {
            'HIGH': ['urgent', 'emergency'],
            'MEDIUM': ['important', 'attention'],
            'LOW': ['update', 'info']
        }
        
    async def process_text(self, text, metadata=None):
        """Process text and send alerts for matched keywords"""
        if not text:  # Skip empty text
            return
            
        for priority, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword.lower() in str(text).lower():
                    await self.alert_system.send_alert(
                        keyword=keyword,
                        text=text,
                        priority=priority,
                        metadata=metadata
                    )