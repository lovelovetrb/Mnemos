from mnemos.core.conversation_service import ConversationService
from tests.fake import FakeAgent


def test_conversation_service() -> None:
    """ユーザーのメッセージに対して、LLMから回答が返る"""
    expect_response = "こんにちは、何かお手伝いできることはありますか。"
    agent = FakeAgent(response=expect_response)
    conversation_service = ConversationService(agent)
    response = conversation_service.handle_message("こんにちは", "test_thread")
    assert response == expect_response


def test_passes_message_to_agent() -> None:
    """ユーザーのメッセージがAgentに渡されていることを確認する"""
    expect_response = "こんにちは。"
    agent = FakeAgent(response=expect_response)
    conversation_service = ConversationService(agent)
    user_message = "テストメッセージ"
    conversation_service.handle_message(user_message, "test_thread")
    assert agent.received_message is not None
    assert agent.received_message.content == user_message
    assert agent.received_thread_id == "test_thread"
