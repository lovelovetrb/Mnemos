from pathlib import Path

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

from mnemos.adapter.langgraph_agent import LangGraphAgent
from mnemos.protocols import Message


def test_conversation_history_is_preserved() -> None:
    """同一thread_idで2回invokeしたとき、会話履歴が4件保持されていること。"""
    llm = FakeListChatModel(responses=["応答1", "応答2"])
    agent = LangGraphAgent(llm, checkpointer=InMemorySaver())
    thread_id = "test_thread"
    expected_history_length = 4

    agent.invoke(Message(content="発言1"), thread_id=thread_id)
    agent.invoke(Message(content="発言2"), thread_id=thread_id)

    state = agent.graph.get_state({"configurable": {"thread_id": thread_id}})
    messages = state.values["messages"]

    assert len(messages) == expected_history_length


def test_checkpointer_can_be_injected() -> None:
    """外部からcheckpointerを注入でき、会話履歴が共有される。"""
    shared_checkpointer = InMemorySaver()
    thread_id = "test_thread"
    expected_history_length = 4

    llm1 = FakeListChatModel(responses=["応答1"])
    agent1 = LangGraphAgent(llm1, checkpointer=shared_checkpointer)
    agent1.invoke(Message(content="発言1"), thread_id=thread_id)

    llm2 = FakeListChatModel(responses=["応答2"])
    agent2 = LangGraphAgent(llm2, checkpointer=shared_checkpointer)
    agent2.invoke(Message(content="発言2"), thread_id=thread_id)

    state = agent2.graph.get_state({"configurable": {"thread_id": thread_id}})
    messages = state.values["messages"]

    assert len(messages) == expected_history_length


def test_conversation_history_persists_with_sqlite(
    tmp_path: Path,
) -> None:
    """SqliteSaverを使うとエージェント再生成後も会話履歴が保持される。"""
    db_path = str(tmp_path / "test.db")
    thread_id = "test_thread"
    expected_history_length = 4

    with SqliteSaver.from_conn_string(db_path) as checkpointer1:
        llm1 = FakeListChatModel(responses=["応答1"])
        agent1 = LangGraphAgent(llm1, checkpointer=checkpointer1)
        agent1.invoke(Message(content="発言1"), thread_id=thread_id)

    with SqliteSaver.from_conn_string(db_path) as checkpointer2:
        llm2 = FakeListChatModel(responses=["応答2"])
        agent2 = LangGraphAgent(llm2, checkpointer=checkpointer2)
        agent2.invoke(Message(content="発言2"), thread_id=thread_id)

        state = agent2.graph.get_state({"configurable": {"thread_id": thread_id}})
        messages = state.values["messages"]

    assert len(messages) == expected_history_length
