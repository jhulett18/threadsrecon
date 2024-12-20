"""
Telegram Alert System Module

This module provides a warning system that sends alerts to Telegram channels/chats.
It supports different priority levels, markdown formatting, and metadata handling.
"""

import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging
from datetime import datetime

class TelegramAlertSystem:
    """
    A class to handle sending formatted alerts to Telegram

    Attributes:
        token (str): Telegram bot API token
        chat_id (str): Target Telegram chat/channel ID
        bot (Bot): Telegram bot instance
        alert_levels (dict): Mapping of priority levels to emoji indicators
    """

    def __init__(self, token, chat_id):
        """
        Initialize the TelegramAlertSystem

        Args:
            token (str): Telegram bot API token
            chat_id (str): Target Telegram chat/channel ID
        """
        self.token = token
        self.chat_id = chat_id
        self.bot = None
        # Define emoji indicators for different alert priorities
        self.alert_levels = {
            'HIGH': '🔴',    # Red circle for high priority
            'MEDIUM': '🟡',  # Yellow circle for medium priority
            'LOW': '🟢'      # Green circle for low priority
        }
        
    async def initialize(self):
        """
        Initialize the Telegram bot instance
        Must be called before sending any messages
        """
        self.bot = Bot(token=self.token)
        
    def escape_markdown(self, text):
        """
        Escape Markdown special characters in text for Telegram's MarkdownV2 format

        Args:
            text (str): Text to escape

        Returns:
            str: Text with escaped special characters

        Note:
            Telegram's MarkdownV2 requires escaping of specific characters
            to prevent formatting issues
        """
        # List of special characters that need to be escaped in MarkdownV2
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        escaped_text = str(text)
        for char in special_chars:
            escaped_text = escaped_text.replace(char, f'\\{char}')
        return escaped_text
        
    def truncate_text(self, text, max_length=200):
        """
        Truncate text while preserving Markdown formatting

        Args:
            text (str): Text to truncate
            max_length (int, optional): Maximum length of resulting text. Defaults to 200.

        Returns:
            str: Truncated text with preserved Markdown formatting

        Note:
            Ensures that Markdown symbols are properly balanced even after truncation
        """
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length].rstrip()
        # Ensure we're not breaking in the middle of a Markdown symbol
        if truncated.count('*') % 2 != 0:
            truncated = truncated.rstrip('*')
        return f"{truncated}..."
        
    async def send_alert(self, keyword, text, priority='LOW', metadata=None):
        """
        Send a formatted alert message to Telegram

        Args:
            keyword (str): Trigger keyword for the alert
            text (str): Main alert message content
            priority (str, optional): Alert priority level ('HIGH', 'MEDIUM', 'LOW'). Defaults to 'LOW'.
            metadata (dict, optional): Additional information to include in the alert. Defaults to None.

        Returns:
            bool: True if message was sent successfully, False otherwise

        Format:
            🔴 *ALERT* 🔴
            *Priority*: HIGH
            *Keyword*: trigger_word
            *Time*: YYYY-MM-DD HH:MM:SS
            *Content*: alert_text
            
            *Additional Info*:
            • key1: value1
            • key2: value2
        """
        if not self.bot:
            await self.initialize()
            
        # Format timestamp with escaped characters for MarkdownV2
        timestamp = datetime.now().strftime('%Y\\-\\%m\\-\\%d %H:%M:%S')
        
        # Get appropriate emoji for priority level
        emoji = self.alert_levels.get(priority.upper(), '⚪')
        
        # Escape all text fields for MarkdownV2
        safe_keyword = self.escape_markdown(str(keyword))
        safe_text = self.escape_markdown(str(text))
        safe_text = self.truncate_text(safe_text)
        
        # Construct message parts
        message_parts = [
            f"{emoji} *ALERT* {emoji}",
            f"*Priority*: {priority}",
            f"*Keyword*: {safe_keyword}",
            f"*Time*: {timestamp}",
            f"*Content*: {safe_text}"
        ]
        
        # Add metadata if provided
        if metadata:
            message_parts.append("\n*Additional Info*:")
            for key, value in metadata.items():
                safe_key = self.escape_markdown(str(key))
                safe_value = self.escape_markdown(str(value))
                # Use bullet point instead of hyphen for lists
                message_parts.append(f"• {safe_key}: {safe_value}")
        
        # Join all parts into final message
        message = '\n'.join(message_parts)
        
        try:
            # Attempt to send the message
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='MarkdownV2'
            )
            return True
        except Exception as e:
            # Log any errors that occur during sending
            logging.error(f"Failed to send Telegram alert: {str(e)}")
            # Log the actual message for debugging purposes
            logging.debug(f"Attempted to send message: {message}")
            return False


class KeywordMonitor:
    """
    Monitor text for specific keywords and trigger alerts

    Attributes:
        alert_system (TelegramAlertSystem): System for sending alerts
        priority_keywords (dict): Mapping of priority levels to keyword lists
    """

    def __init__(self, telegram_token, chat_id, priority_keywords=None):
        """
        Initialize the KeywordMonitor

        Args:
            telegram_token (str): Telegram bot API token
            chat_id (str): Target Telegram chat/channel ID
            priority_keywords (dict, optional): Mapping of priority levels to keyword lists.
                Defaults to predefined set if None.
        """
        self.alert_system = TelegramAlertSystem(telegram_token, chat_id)
        # Default priority keywords if none provided
        self.priority_keywords = priority_keywords or {
            'HIGH': ['urgent', 'emergency'],
            'MEDIUM': ['important', 'attention'],
            'LOW': ['update', 'info']
        }
        
    async def process_text(self, text, metadata=None):
        """
        Process text and send alerts for matched keywords

        Args:
            text (str): Text to monitor for keywords
            metadata (dict, optional): Additional information to include in alerts.
                Defaults to None.

        Note:
            Checks text against all priority levels and their keywords
            Sends alert through TelegramAlertSystem when matches are found
        """
        if not text:  # Skip empty text
            return
            
        # Check each priority level and its keywords
        for priority, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword.lower() in str(text).lower():
                    await self.alert_system.send_alert(
                        keyword=keyword,
                        text=text,
                        priority=priority,
                        metadata=metadata
                    )