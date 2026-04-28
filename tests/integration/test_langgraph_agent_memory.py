from langchain_core.language_models.fake_chat_models import FakeListChatModel

from mnemos.adapter.langgraph_agent import LangGraphAgent
from mnemos.protocols import Message


def test_conversation_history_is_preserved() -> None:
    """同一thread_idで2回invokeしたとき、会話履歴が4件保持されていること。"""
    llm = FakeListChatModel(responses=["応答1", "応答2"])
    agent = LangGraphAgent(llm)
    thread_id = "test_thread"
    expected_history_length = 4

    agent.invoke(Message(content="発言1"), thread_id=thread_id)
    agent.invoke(Message(content="発言2"), thread_id=thread_id)

    state = agent.graph.get_state({"configurable": {"thread_id": thread_id}})
    messages = state.values["messages"]

    assert len(messages) == expected_history_length
