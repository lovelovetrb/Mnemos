"""MessagingGatewayのユニットテスト"""

import pytest

from mnemos.core.conversation_service import ConversationService
from tests.fake import FakeAgent, FakeMessagingGateway


@pytest.mark.asyncio
async def test_gateway_is_not_running_by_default() -> None:
    """初期状態ではゲートウェイは起動していない"""
    agent = FakeAgent(response="ok")
    service = ConversationService(agent)
    gateway = FakeMessagingGateway(conversation_service=service)
    assert not gateway.is_running


@pytest.mark.asyncio
async def test_start_sets_running() -> None:
    """startを呼ぶとゲートウェイが起動状態になる"""
    agent = FakeAgent(response="ok")
    service = ConversationService(agent)
    gateway = FakeMessagingGateway(conversation_service=service)
    await gateway.start()
    assert gateway.is_running


@pytest.mark.asyncio
async def test_stop_sets_not_running() -> None:
    """stopを呼ぶとゲートウェイが停止状態になる"""
    agent = FakeAgent(response="ok")
    service = ConversationService(agent)
    gateway = FakeMessagingGateway(conversation_service=service)
    await gateway.start()
    await gateway.stop()
    assert not gateway.is_running
