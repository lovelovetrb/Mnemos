"""MessagingGatewayの結合テスト"""

import pytest

from mnemos.core.conversation_service import ConversationService
from tests.fake import FakeAgent, FakeMessagingGateway


@pytest.mark.asyncio
async def test_handle_message_returns_agent_response() -> None:
    """メッセージを受け取り、Agentからの応答を返す"""
    expected = "こんにちは、何かお手伝いできることはありますか。"
    agent = FakeAgent(response=expected)
    service = ConversationService(agent)
    gateway = FakeMessagingGateway(conversation_service=service)
    response = await gateway.handle_message("こんにちは", "test_thread")
    assert response == expected


@pytest.mark.asyncio
async def test_handle_message_passes_correct_thread_id() -> None:
    """thread_idがAgentまで正しく伝播される"""
    agent = FakeAgent(response="ok")
    service = ConversationService(agent)
    gateway = FakeMessagingGateway(conversation_service=service)
    await gateway.handle_message("テスト", "thread_123")
    assert agent.received_thread_id == "thread_123"
