import pytest
from langchain_core.language_models.fake_chat_models import (
    FakeListChatModel,
)
from langchain_core.messages import AIMessage

from mnemos.adapter.langgraph_agent import LangGraphAgent
from mnemos.protocols import Message
from tests.fake import FakeLLM, fake_error_tool, fake_tool


@pytest.fixture
def setup_mock_llm():
    def _setup(tool_name: str) -> FakeLLM:
        return FakeLLM(
            responses=[
                AIMessage(
                    content="ツールが呼び出されました!",
                    tool_calls=[
                        {
                            "id": "call_1",
                            "name": tool_name,
                            "args": {},
                        }
                    ],
                ),
                AIMessage(content="こんにちは!"),
            ]
        )

    return _setup


def test_ok_response_from_langgraph_agent() -> None:
    expected_response = "こんにちは!"
    llm = FakeListChatModel(responses=[expected_response])
    agent = LangGraphAgent(llm)
    agent_response = agent.invoke(
        Message(content="Hello, Agent!"), thread_id="test_thread"
    )
    assert agent_response.content == expected_response


def test_tool_called_by_langgraph_agent(setup_mock_llm) -> None:
    expected_response = "こんにちは!"
    llm = setup_mock_llm("fake_tool")
    agent = LangGraphAgent(llm, tools=[fake_tool])
    agent_response = agent.invoke(
        Message(content="Call the tool!"), thread_id="test_thread"
    )
    assert agent_response.content == expected_response


def test_tool_called_invoke_error(setup_mock_llm) -> None:
    expected_response = "こんにちは!"
    llm = setup_mock_llm("fake_error_tool")
    agent = LangGraphAgent(llm, tools=[fake_error_tool])
    agent_response = agent.invoke(
        Message(content="Call the tool!"), thread_id="test_thread"
    )
    assert agent_response.content == expected_response


def test_invalid_tool_name(setup_mock_llm) -> None:
    llm = setup_mock_llm("non_existent_tool")
    agent = LangGraphAgent(llm, tools=[fake_tool])
    agent_response = agent.invoke(
        Message(content="Call the tool!"), thread_id="test_thread"
    )
    assert agent_response.content == "こんにちは!"
