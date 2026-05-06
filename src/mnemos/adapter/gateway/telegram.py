"""Telegramを用いたMessagingGatewayの具体実装"""

import asyncio
import logging

from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    Updater,
    filters,
)

from mnemos.core.conversation_service import ConversationService
from mnemos.protocols import MessagingGateway

logger = logging.getLogger(__name__)


class TelegramGateway(MessagingGateway):
    """Telegram Botを用いたMessagingGatewayの具体実装"""

    def __init__(
        self,
        bot_token: str,
        conversation_service: ConversationService,
    ) -> None:
        """TelegramGatewayのコンストラクタ"""
        self.conversation_service = conversation_service
        self.app = Application.builder().token(bot_token).build()
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_message)
        )

    async def start(self) -> None:
        """Telegram Botのポーリングを開始する"""
        await self.app.initialize()
        await self.app.start()
        await self._get_updater().start_polling()
        logger.info("Telegram Bot started")

    async def stop(self) -> None:
        """Telegram Botのポーリングを停止する"""
        await self._get_updater().stop()
        await self.app.stop()
        await self.app.shutdown()
        logger.info("Telegram Bot stopped")

    def _get_updater(self) -> Updater:
        """Updaterを取得する。存在しない場合はRuntimeErrorを送出する。"""
        if self.app.updater is None:
            msg = "Updater is not available"
            raise RuntimeError(msg)
        return self.app.updater

    async def handle_message(self, message: str, thread_id: str) -> str:
        """メッセージを受信して応答を返す"""
        return await asyncio.to_thread(
            self.conversation_service.handle_message,
            message,
            thread_id,
        )

    async def _on_message(
        self,
        update: Update,
        _context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Telegramからメッセージを受信したときのコールバック"""
        if update.message is None or update.message.text is None:
            return

        thread_id = str(update.message.chat_id)
        response = await self.handle_message(update.message.text, thread_id)
        await update.message.reply_text(response)
