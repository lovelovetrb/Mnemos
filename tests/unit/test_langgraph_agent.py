from langchain_core.language_models.fake_chat_models import FakeListChatModel

from mnemos.adapter.langgraph_agent import LangGraphAgent
from mnemos.protocols import Message


def test_ok_response_from_langgraph_agent() -> None:
    expected_response = "こんにちは!"
    llm = FakeListChatModel(responses=[expected_response])
    agent = LangGraphAgent(llm)
    agent_response = agent.invoke(
        Message(content="Hello, Agent!"), thread_id="test_thread"
    )
    assert agent_response.content == expected_response
