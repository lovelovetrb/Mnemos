"""MessagingGatewayのFake実装"""

import asyncio

from mnemos.core.conversation_service import ConversationService
from mnemos.protocols import MessagingGateway


class FakeMessagingGateway(MessagingGateway):
    """テスト用のMessagingGateway実装"""

    def __init__(self, conversation_service: ConversationService) -> None:
        self.conversation_service = conversation_service
        self.is_running = False

    async def start(self) -> None:
        """ゲートウェイを起動する"""
        self.is_running = True

    async def stop(self) -> None:
        """ゲートウェイを停止する"""
        self.is_running = False

    async def handle_message(self, message: str, thread_id: str) -> str:
        """メッセージを受信して応答を返す"""
        return await asyncio.to_thread(
            self.conversation_service.handle_message,
            message,
            thread_id,
        )
